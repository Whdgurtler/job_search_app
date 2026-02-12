"""Configuration for job search agent."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # Optional, for HF Inference API

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and good quality
LLM_PROVIDER = "huggingface"  # "anthropic", "openai", or "huggingface"
LLM_MODEL = "Qwen/Qwen2.5-72B-Instruct"  # Large model via HuggingFace Inference API

# Hugging Face Options
# For large models (>7B params), use the Inference API (USE_LOCAL_MODEL = False)
# For small models, local mode works — set True and pick e.g. "Qwen/Qwen2.5-7B-Instruct"
USE_LOCAL_MODEL = False  # 72B model requires Inference API, too large for local

# Auto-detect device (GPU if available, otherwise CPU)
# Lazy import to avoid slow torch load at startup
def _detect_device():
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device auto-detected: {device}")
        if device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
        return device
    except Exception as e:
        print(f"Warning: CUDA/torch detection failed ({e}), using CPU")
        return "cpu"

DEVICE = _detect_device()

# Job Level Hierarchy
JOB_LEVELS = {
    "individual_contributor": [
        "Intern",
        "Junior",
        "Mid-Level",
        "Senior",
        "Staff",
        "Principal",
        "Distinguished"
    ],
    "management": [
        "Team Lead",
        "Manager",
        "Senior Manager",
        "Director",
        "Senior Director",
        "VP",
        "SVP",
        "C-Suite"
    ]
}

# Matching Weights
WEIGHTS = {
    "skill_match": 0.35,
    "semantic_similarity": 0.25,
    "level_fit": 0.25,
    "growth_potential": 0.15
}

# Stretch Role Criteria
STRETCH_LEVELS_UP = 2  # Look up to 2 levels above current
MIN_SKILL_MATCH_STRETCH = 0.65  # 65% skill match for stretch roles
