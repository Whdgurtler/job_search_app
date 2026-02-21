"""Resume service — file upload, parsing, and management."""

import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root so we can import existing parsers
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from resume_file_parser import ResumeFileParser
from resume_parser import ResumeParser

from ..models.resume import Resume
from .storage_service import get_storage_service


class ResumeService:
    """Handles resume upload, parsing, and retrieval."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()

    async def upload_and_parse(
        self,
        user_id: UUID,
        file_name: str,
        file_data: bytes,
        content_type: str,
    ) -> Resume:
        """Upload file to storage, extract text, parse with LLM, save to DB."""

        # 1. Upload to storage (GCS or local)
        file_url = self.storage.upload_resume(
            str(user_id), file_name, file_data, content_type,
        )

        # 2. Write to temp file for parser (parsers expect file paths)
        ext = Path(file_name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        try:
            # 3. Extract raw text
            raw_text = ResumeFileParser.parse(tmp_path)
            if not ResumeFileParser.validate_resume(raw_text):
                raise ValueError("File does not appear to be a valid resume")

            # 4. Parse structured data with LLM
            parser = ResumeParser()
            resume_data = parser.parse(raw_text)
            parsed_dict = resume_data.model_dump()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        # 5. Deactivate previous active resumes
        result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.is_active == True,
            )
        )
        for old_resume in result.scalars().all():
            old_resume.is_active = False

        # 6. Create resume record
        resume = Resume(
            user_id=user_id,
            file_url=file_url,
            file_name=file_name,
            file_type=ext.lstrip("."),
            file_size_bytes=len(file_data),
            parsed_data=parsed_dict,
            current_title=resume_data.current_title,
            experience_years=resume_data.experience_years,
            skills=resume_data.skills,
            is_active=True,
            parsed_at=datetime.now(timezone.utc),
        )
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)

        return resume

    async def list_resumes(self, user_id: UUID) -> list[Resume]:
        """Get all resumes for a user, newest first."""
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def get_resume(self, user_id: UUID, resume_id: UUID) -> Resume | None:
        """Get a specific resume."""
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_resume(self, user_id: UUID) -> Resume | None:
        """Get the currently active resume for a user."""
        result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def set_active(self, user_id: UUID, resume_id: UUID) -> Resume | None:
        """Set a specific resume as active (deactivates others)."""
        # Deactivate all
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id, Resume.is_active == True)
        )
        for r in result.scalars().all():
            r.is_active = False

        # Activate target
        resume = await self.get_resume(user_id, resume_id)
        if resume:
            resume.is_active = True
            await self.db.commit()
            await self.db.refresh(resume)
        return resume

    async def get_company_suggestions(self, user_id: UUID) -> list[dict]:
        """Generate company suggestions based on the user's active resume."""
        resume = await self.get_active_resume(user_id)
        if not resume or not resume.parsed_data:
            return []

        parsed = resume.parsed_data
        industries = parsed.get("industries", [])
        current_title = parsed.get("current_title", "")
        current_company = parsed.get("current_company", "")
        past_companies = parsed.get("past_companies", [])
        past_titles = parsed.get("past_titles", [])
        skills = parsed.get("skills", [])

        if not industries and not current_title:
            return []

        context = f"Current title: {current_title}\n"
        if current_company:
            context += f"Most recent company: {current_company}\n"
        if past_companies:
            context += f"Previous companies: {', '.join(past_companies[:5])}\n"
        if past_titles:
            context += f"Past titles: {', '.join(past_titles[:5])}\n"
        if industries:
            context += f"Industries: {', '.join(industries)}\n"
        if skills:
            context += f"Key skills: {', '.join(skills[:10])}\n"

        prompt = f"""Based on this candidate's background, suggest 10-15 companies they should target in their job search. Focus on companies that:
1. Are in the same or adjacent industries as their most recent company
2. Are similar in size and type to {current_company or 'companies they have worked at'} (e.g., if they worked at a regional bank, suggest other regional banks of similar size)
3. Would value their specific skill set
4. Include a mix of direct competitors and adjacent companies

Candidate background:
{context}

Return ONLY a JSON array of objects, no other text:
[
  {{"name": "Company Name", "reason": "Brief reason why this is a good fit"}},
  ...
]"""

        try:
            from config import LLM_PROVIDER, LLM_MODEL
            from llm_analyzer import LLMAnalyzer

            llm = LLMAnalyzer(provider=LLM_PROVIDER, model=LLM_MODEL)
            response = llm.analyze(prompt, max_tokens=1000)

            if not response:
                return []

            import json
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(response)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Company suggestion failed: {e}")
            return []

    async def delete_resume(self, user_id: UUID, resume_id: UUID) -> bool:
        """Delete a resume and its file from storage."""
        resume = await self.get_resume(user_id, resume_id)
        if not resume:
            return False

        # Delete from storage
        try:
            self.storage.delete_file(resume.file_url)
        except Exception:
            pass  # File might already be gone

        await self.db.delete(resume)
        await self.db.commit()
        return True
