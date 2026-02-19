"""LLM-based analysis for career progression and stretch roles."""
from typing import Dict, Optional
import anthropic
import openai
from config import (
    ANTHROPIC_API_KEY, OPENAI_API_KEY, HUGGINGFACE_API_KEY, MOONSHOT_API_KEY,
    LLM_PROVIDER, LLM_MODEL, USE_LOCAL_MODEL, DEVICE
)


def _check_hf_available():
    """Lazily check if transformers/torch are available (avoids slow import at module load)."""
    try:
        import transformers  # noqa: F401
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


class LLMAnalyzer:
    """Use LLM for intelligent career analysis."""
    
    def __init__(self, provider: str = LLM_PROVIDER, model: str = LLM_MODEL):
        self.provider = provider
        self.model = model
        self.hf_pipeline = None
        
        if provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        elif provider == "openai":
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        elif provider == "kimi":
            self.client = openai.OpenAI(
                api_key=MOONSHOT_API_KEY,
                base_url="https://api.moonshot.cn/v1"
            )
        elif provider == "huggingface":
            if USE_LOCAL_MODEL and not _check_hf_available():
                raise ImportError("transformers and torch are required for local HuggingFace models. Install with: pip install transformers torch")

            if USE_LOCAL_MODEL:
                print(f"Loading HuggingFace model: {model}...")
                self._init_local_model()
            else:
                print(f"Using HuggingFace Inference API for: {model}")
                self.client = None  # Will use API calls
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_local_model(self):
        """Initialize local HuggingFace model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch

            device = DEVICE if torch.cuda.is_available() or DEVICE == "cpu" else "cpu"
            print(f"  Device: {device}")

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.model, trust_remote_code=True)

            # Load model with memory optimization
            model = AutoModelForCausalLM.from_pretrained(
                self.model,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )

            # Create pipeline
            self.hf_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            print("  Model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load HuggingFace model: {e}")
    
    def analyze(self, prompt: str, max_tokens: int = 2000) -> str:
        """Send prompt to LLM and get response."""
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.provider == "kimi":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        elif self.provider == "huggingface":
            if USE_LOCAL_MODEL and self.hf_pipeline:
                # Local model inference
                messages = [{"role": "user", "content": prompt}]
                outputs = self.hf_pipeline(
                    messages,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                return outputs[0]["generated_text"][-1]["content"]
            else:
                # Use HuggingFace Serverless Inference API (new endpoint)
                import requests
                api_url = "https://router.huggingface.co/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }

                try:
                    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        # Extract message from new API format
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"]
                        return str(result)
                    else:
                        # If API fails, return empty to trigger fallback
                        print(f"   Warning: HuggingFace API error: {response.status_code}")
                        if response.status_code == 400:
                            print(f"   Model '{self.model}' may not be supported on Serverless API")
                        return None
                except Exception as e:
                    print(f"   Warning: HuggingFace API request failed: {e}")
                    return None
    
    def assess_stretch_fit(
        self,
        resume_summary: str,
        job_description: str,
        current_level: str,
        target_level: str
    ) -> Dict:
        """
        Assess if candidate is ready for a stretch role.
        
        Returns dict with:
        - is_stretch_fit: bool
        - confidence: float (0-1)
        - reasoning: str
        - missing_skills: list
        - transferable_skills: list
        """
        prompt = f"""You are a career advisor AI. Assess if this candidate is ready for a stretch role one level above their current position.

Current Level: {current_level}
Target Level: {target_level}

Resume Summary:
{resume_summary}

Job Description:
{job_description}

Analyze:
1. Is this a reasonable stretch role? (not too far above current level)
2. Does the candidate have 65-80% of required skills?
3. Are missing skills learnable vs. hard requirements (certifications, years)?
4. Does the candidate show growth trajectory and readiness signals?

Provide your assessment in this JSON format:
{{
  "is_stretch_fit": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation",
  "missing_skills": ["skill1", "skill2"],
  "transferable_skills": ["skill1", "skill2"],
  "readiness_signals": ["signal1", "signal2"]
}}

Return ONLY valid JSON, no other text."""

        response = self.analyze(prompt)
        
        import json
        try:
            return json.loads(response)
        except:
            return {
                "is_stretch_fit": False,
                "confidence": 0.0,
                "reasoning": "Failed to analyze",
                "missing_skills": [],
                "transferable_skills": [],
                "readiness_signals": []
            }
    
    def explain_match(
        self,
        resume_summary: str,
        job_description: str,
        match_scores: Dict
    ) -> str:
        """Generate human-readable explanation of why job matches."""
        prompt = f"""Explain why this job is a good match for this candidate. Be specific and encouraging.

Resume Summary:
{resume_summary}

Job Description:
{job_description}

Match Scores:
- Skill Match: {match_scores.get('skill_match', 0):.0%}
- Semantic Similarity: {match_scores.get('semantic_similarity', 0):.0%}
- Level Fit: {match_scores.get('level_fit', 0):.0%}

Write a 2-3 sentence explanation highlighting:
1. Key matching skills/experience
2. Why this is a good next step
3. Any stretch opportunities

Keep it concise and actionable."""

        return self.analyze(prompt, max_tokens=200)
    
    def generate_career_insights(self, resume_summary: str, target_roles: list) -> str:
        """Generate career development insights."""
        prompt = f"""Based on this resume, provide career development advice for moving into these target roles:

Resume Summary:
{resume_summary}

Target Roles:
{', '.join(target_roles)}

Provide:
1. Skills to develop (2-3 most important)
2. Experience gaps to fill
3. Recommended timeline
4. Specific actionable steps

Keep response under 150 words."""

        return self.analyze(prompt, max_tokens=300)
