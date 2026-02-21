"""Resume parsing and analysis."""
from typing import Dict, List, Optional
from pydantic import BaseModel


class ResumeData(BaseModel):
    """Structured resume data."""
    skills: List[str]
    experience_years: float
    current_title: str
    current_company: str = ""
    current_level: str
    past_titles: List[str]
    past_companies: List[str] = []
    industries: List[str]
    achievements: List[str]
    has_leadership_experience: bool
    team_size_managed: Optional[int] = None
    education: List[str]
    certifications: List[str]
    
    
class ResumeParser:
    """Parse resume text using LLM."""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
    def parse(self, resume_text: str) -> ResumeData:
        """Parse resume text into structured data using LLM."""
        prompt = f"""Analyze this resume and extract ONLY the requested information. Return valid JSON.

CRITICAL INSTRUCTIONS:
- current_title: Extract ONLY the job title from the most recent position (e.g., "Data Scientist", "Senior Software Engineer", "Product Manager"). DO NOT include job descriptions or responsibilities.
- current_company: The company name for the most recent position (e.g., "Google", "First Horizon Bank").
- experience_years: Count total years of professional work experience (number only, e.g., 5.0)
- education: Extract ALL degrees with field (e.g., ["MS Artificial Intelligence", "BS Mathematics"]). List BOTH Bachelor's AND Master's/PhD if present. Use format like "MS" or "Master of Science", not "m.s."
- current_level: One of: Intern, Junior, Mid-Level, Senior, Staff, Principal, Team Lead, Manager, Senior Manager, Director, VP, C-Suite
- past_companies: List of previous employer company names (not the current one).

Resume:
{resume_text[:3000]}

Return ONLY this JSON format (no markdown, no extra text):
{{
  "skills": ["Python", "SQL", "Machine Learning"],
  "experience_years": 5.0,
  "current_title": "Senior Data Scientist",
  "current_company": "Acme Corp",
  "current_level": "Senior",
  "past_titles": ["Data Analyst", "Junior Data Scientist"],
  "past_companies": ["Previous Corp", "First Job Inc"],
  "industries": ["Technology", "Finance"],
  "achievements": ["Led team of 5", "Increased revenue by 20%"],
  "has_leadership_experience": true,
  "team_size_managed": 5,
  "education": ["MS Artificial Intelligence", "BS Mathematics"],
  "certifications": ["AWS Certified"]
}}"""

        response = self.llm_client.analyze(prompt, max_tokens=1000)
        
        # If LLM returns None (API failed), use fallback immediately
        if response is None:
            print("   Warning: Could not parse resume with LLM (API unavailable)")
            print("   Using fallback keyword extraction...")
            return self._fallback_parse(resume_text)
        
        # Parse LLM response into ResumeData
        import json
        import re
        
        try:
            # Try to extract JSON if wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Remove any leading/trailing text
            response = response.strip()
            if not response.startswith('{'):
                start = response.find('{')
                if start != -1:
                    response = response[start:]
            if not response.endswith('}'):
                end = response.rfind('}')
                if end != -1:
                    response = response[:end+1]
            
            data = json.loads(response)
            
            # Validate the parsed data
            if not self._validate_resume_data(data, resume_text):
                print("   Warning: LLM returned invalid data, using fallback...")
                return self._fallback_parse(resume_text)
            
            return ResumeData(**data)
        except Exception as e:
            print(f"   Warning: LLM parsing failed ({e}), using fallback...")
            # Fallback to regex-based extraction
            return self._fallback_parse(resume_text)
    
    def _validate_resume_data(self, data: dict, resume_text: str) -> bool:
        """Validate that extracted resume data makes sense."""
        # Check if current_title is reasonable (not too long, not a sentence)
        title = data.get('current_title', '')
        if len(title) > 60 or len(title.split()) > 8:
            print(f"   WARNING  Title too long or malformed: {title[:50]}...")
            return False
        
        # Check if title contains common job description words (indicates wrong extraction)
        bad_words = ['develop', 'responsible', 'lead the', 'oversee', 'manage the', 'ensure', 'implement']
        if any(word in title.lower() for word in bad_words):
            print(f"   WARNING  Title contains job description: {title[:50]}...")
            return False
        
        # Check if experience years is reasonable
        exp_years = data.get('experience_years', 0)
        if exp_years < 0 or exp_years > 50:
            print(f"   WARNING  Experience years unreasonable: {exp_years}")
            return False
        
        # Check if education format is reasonable
        education = data.get('education', [])
        if education:
            for edu in education:
                if len(edu) > 100:  # Education entry too long
                    print(f"   WARNING  Education entry too long: {edu[:50]}...")
                    return False
        
        return True
    
    def _fallback_parse_old(self, resume_text: str) -> ResumeData:
        """Old fallback that's replaced."""
        prompt = f"""Analyze this resume and extract structured information in JSON format.

Resume:
{resume_text[:3000]}

Extract the following and return ONLY valid JSON (no markdown, no explanation):
{{
  "skills": ["list", "of", "skills"],
  "experience_years": 5.0,
  "current_title": "Most recent job title",
  "current_level": "Senior",
  "past_titles": ["previous", "titles"],
  "industries": ["Technology"],
  "achievements": ["key accomplishments"],
  "has_leadership_experience": true,
  "team_size_managed": 5,
  "education": ["BS Computer Science"],
  "certifications": []
}}

Valid levels: Intern, Junior, Mid-Level, Senior, Staff, Principal, Team Lead, Manager, Senior Manager, Director, VP, C-Suite"""

        response = self.llm_client.analyze(prompt, max_tokens=1000)
        
        # Parse LLM response into ResumeData
        import json
        import re
        
        try:
            # Try to extract JSON if wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            # Remove any leading/trailing text
            response = response.strip()
            if not response.startswith('{'):
                start = response.find('{')
                if start != -1:
                    response = response[start:]
            if not response.endswith('}'):
                end = response.rfind('}')
                if end != -1:
                    response = response[:end+1]
            
            data = json.loads(response)
            return ResumeData(**data)
        except Exception as e:
            print(f"Warning: LLM parsing failed ({e}), using fallback...")
            # Fallback to regex-based extraction
            return self._fallback_parse(resume_text)
    
    def _fallback_parse(self, resume_text: str) -> ResumeData:
        """Improved fallback parser with better title and education extraction."""
        import re
        
        # Extract skills (prioritize advanced/specialized skills)
        common_skills = ['Agentic AI', 'Large Language Models', 'LLMs', 'Generative AI', 'GPT', 
                        'Transformer Models', 'Prompt Engineering', 'RAG', 'Fine-tuning', 'Model Deployment',
                        'MLOps', 'Reinforcement Learning', 'Deep Reinforcement Learning', 'RLHF',
                        'Deep Learning', 'Machine Learning', 'NLP', 'Computer Vision', 'Neural Networks',
                        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Hugging Face',
                        'Python', 'R', 'Scala', 'Java', 'C++', 'JavaScript', 'TypeScript', 'Go',
                        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Spark', 'Hadoop', 'Kafka',
                        'Data Engineering', 'ETL', 'Data Pipeline', 'Data Analysis', 'Statistics',
                        'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'React', 'Node.js', 
                        'Tableau', 'Power BI', 'Excel', 'Git', 'CI/CD', 'REST API', 'Microservices',
                        'Leadership', 'Agile', 'Pandas', 'NumPy']
        
        skills = [skill for skill in common_skills if skill.lower() in resume_text.lower()]
        
        # Extract experience years - look for explicit mentions
        experience_years = 5.0  # Default
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+in',
            r'total[:\s]+(\d+)\+?\s*years?'
        ]
        for pattern in year_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                experience_years = float(match.group(1))
                print(f"   INFO  Extracted experience: {experience_years} years")
                break
        
        # Extract current title - improved patterns
        current_title = "Data Scientist"  # Default
        
        # Look for explicit "Current:" or "Present:" sections
        current_patterns = [
            r'(?:Current|Present)[:\s]+([A-Z][^\n,]+?)(?:\s+at|\s+\||\n|,)',
            r'(?:Current|Present)[:\s]+([A-Z][^\n]+?)(?:\n)',
        ]
        
        for pattern in current_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                potential_title = match.group(1).strip()
                # Clean up the title
                potential_title = re.sub(r'\s+', ' ', potential_title)
                # Only accept if it's not too long and doesn't contain job description words
                if len(potential_title) < 50 and not any(word in potential_title.lower() for word in ['develop', 'responsible', 'lead the']):
                    current_title = potential_title
                    print(f"   INFO  Extracted title: {current_title}")
                    break
        
        # If no explicit "Current:" found, look for common job titles
        if current_title == "Data Scientist":
            title_patterns = [
                r'((?:Senior|Staff|Principal|Lead|Chief)?\s*(?:Data Scientist|Software Engineer|Product Manager|Engineering Manager|Data Engineer|ML Engineer|Data Analyst|Business Analyst|DevOps Engineer|Solutions Architect))',
            ]
            for pattern in title_patterns:
                matches = re.findall(pattern, resume_text, re.IGNORECASE)
                if matches:
                    current_title = matches[0].strip()
                    print(f"   INFO  Inferred title: {current_title}")
                    break
        
        # Determine level from title
        current_level = "Mid-Level"
        title_lower = current_title.lower()
        if any(word in title_lower for word in ['senior', 'sr.', 'sr ']):
            current_level = "Senior"
        elif any(word in title_lower for word in ['principal', 'staff']):
            current_level = "Principal"
        elif any(word in title_lower for word in ['lead', 'manager']):
            current_level = "Manager"
        elif any(word in title_lower for word in ['director']):
            current_level = "Director"
        elif any(word in title_lower for word in ['junior', 'jr.', 'jr ', 'associate']):
            current_level = "Junior"
        elif any(word in title_lower for word in ['chief', 'vp', 'vice president']):
            current_level = "VP"
        
        print(f"   INFO  Determined level: {current_level}")
        
        # Extract education - improved patterns
        education = []
        
        # More comprehensive patterns to catch all degree formats
        edu_patterns = [
            # Pattern 1: M.S., M.A., B.S., B.A. with dots (most specific first)
            r'(M\.S\.\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(M\.A\.\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(B\.S\.\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(B\.A\.\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(Ph\.D\.\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            # Pattern 2: MS, MA, BS, BA without dots
            r'(MS\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(MA\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(MBA)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(BS\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(BA\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(PhD\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            # Pattern 3: Full degree names
            r'(Master\s+of\s+Science\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(Master\s+of\s+Arts\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(Bachelor\s+of\s+Science\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
            r'(Bachelor\s+of\s+Arts\s+(?:in\s+)?[A-Z][a-zA-Z\s]+?)(?:\s+from|\s+,|\s+-|\s+at|\n|$)',
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                clean_edu = match.strip()
                # Remove trailing conjunctions, prepositions, or articles
                clean_edu = re.sub(r'\s+(and|with|from|the|at|by|as|for)$', '', clean_edu, flags=re.IGNORECASE)
                # Remove trailing punctuation
                clean_edu = clean_edu.rstrip('.,;:')
                
                # Validate education entry - must be reasonable length and format
                words = clean_edu.split()
                # Should have 1-7 words (e.g., "MBA", "MS Computer Science", "Master of Science in Artificial Intelligence")
                if 1 <= len(words) <= 7 and len(clean_edu) < 80:
                    # Check it's not a sentence (no job description verbs)
                    bad_words = ['models', 'forecast', 'challenger', 'financial', 
                                'develop', 'lead', 'manage', 'ensure', 'work', 'responsible']
                    if not any(word in clean_edu.lower() for word in bad_words):
                        # Normalize degree format (e.g., "m.s." -> "MS", "M.S." -> "MS")
                        clean_edu = re.sub(r'\b([BMPhD])\.([SsAa])\.\b', lambda m: m.group(1).upper() + m.group(2).upper(), clean_edu)
                        # Capitalize properly
                        if clean_edu.upper() in ['MBA', 'MS', 'MA', 'BS', 'BA', 'PHD']:
                            clean_edu = clean_edu.upper()
                        education.append(clean_edu)
        
        education = list(set(education))  # Deduplicate
        
        # Sort education by level (PhD > Master's > Bachelor's) and limit to 2
        def edu_priority(edu_str):
            edu_lower = edu_str.lower()
            if 'phd' in edu_lower or 'ph.d' in edu_lower or 'doctor' in edu_lower:
                return 0
            elif 'ms' in edu_lower or 'm.s' in edu_lower or 'ma' in edu_lower or 'm.a' in edu_lower or 'mba' in edu_lower or 'master' in edu_lower:
                return 1
            elif 'bs' in edu_lower or 'b.s' in edu_lower or 'ba' in edu_lower or 'b.a' in edu_lower or 'bachelor' in edu_lower:
                return 2
            return 3
        
        education.sort(key=edu_priority)
        education = education[:2]  # Show top 2 degrees
        
        # If no valid education found, look for university names as fallback
        if not education:
            university_pattern = r'(University\s+of\s+[A-Z][a-z]+|[A-Z][a-z]+\s+University|[A-Z][a-z]+\s+College|[A-Z][a-z]+\s+Institute\s+of\s+Technology)'
            unis = re.findall(university_pattern, resume_text)
            if unis:
                education = [unis[0]]
        
        if education:
            print(f"   INFO  Extracted education: {education}")
        
        # Check for leadership experience
        has_leadership = any(word in resume_text.lower() for word in 
                           ['led team', 'managed team', 'leadership', 'supervised', 'mentored'])
        
        # Extract team size
        team_size = None
        team_patterns = [
            r'(?:team|group)\s+of\s+(\d+)',
            r'managed\s+(\d+)\s+(?:people|engineers|developers)',
            r'led\s+(\d+)\s+(?:people|engineers|developers)'
        ]
        for pattern in team_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                team_size = int(match.group(1))
                break
        
        return ResumeData(
            skills=skills[:20] if skills else ['Data Analysis', 'Python', 'SQL'],
            experience_years=experience_years,
            current_title=current_title,
            current_level=current_level,
            past_titles=[],
            industries=['Technology'],
            achievements=[],
            has_leadership_experience=has_leadership,
            team_size_managed=team_size,
            education=education if education else ['Not specified'],
            certifications=[]
        )
    
    def detect_growth_signals(self, resume_data: ResumeData) -> Dict[str, any]:
        """Detect signals that candidate is ready for next level."""
        signals = {
            "promotions": len(set(resume_data.past_titles)) > 1,
            "long_tenure": resume_data.experience_years >= 3,
            "leadership_mentions": resume_data.has_leadership_experience,
            "scope_expansion": False,  # Would analyze achievements for scope growth
            "ready_score": 0.0
        }
        
        # Calculate readiness score
        score = 0.0
        if signals["promotions"]:
            score += 0.3
        if signals["long_tenure"]:
            score += 0.3
        if signals["leadership_mentions"]:
            score += 0.4
            
        signals["ready_score"] = score
        return signals
