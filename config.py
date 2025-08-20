"""
Configuration module for SIA integrations.

Supports environment variables or direct assignment for:
- Vector DB selection (FAISS or Pinecone)
- Pinecone API key and environment
- LLM provider (Hugging Face or OpenAI)
- Hugging Face model name and API key
- OpenAI model name and API key
"""

import os

# Vector DB config
VECTOR_DB = os.getenv("SIA_VECTOR_DB", "faiss")  # "faiss" or "pinecone"
PINECONE_API_KEY = os.getenv("SIA_PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("SIA_PINECONE_ENV", "")

# Persistent storage config
MEMORY_STORAGE_PATH = os.getenv("SIA_MEMORY_STORAGE_PATH", "./sia_data/memories.json")
ANALYSIS_REPORTS_PATH = os.getenv("SIA_ANALYSIS_REPORTS_PATH", "./sia_data/analysis_reports")
PR_RESULTS_PATH = os.getenv("SIA_PR_RESULTS_PATH", "./sia_data/pr_results")

# LLM config
LLM_PROVIDER = os.getenv("SIA_LLM_PROVIDER", "openai")  # "openai", "huggingface", "openrouter", "anthropic", or "lmstudio"
OPENAI_API_KEY = os.getenv("SIA_OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("SIA_OPENAI_MODEL", "gpt-3.5-turbo")
HF_API_KEY = os.getenv("SIA_HF_API_KEY", "")
HF_MODEL = os.getenv("SIA_HF_MODEL", "gpt2")
OPENROUTER_API_KEY = os.getenv("SIA_OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("SIA_OPENROUTER_MODEL", "openrouter/codellama-34b")
ANTHROPIC_API_KEY = os.getenv("SIA_ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("SIA_ANTHROPIC_MODEL", "claude-3-haiku-20240307")
LMSTUDIO_API_URL = os.getenv("SIA_LMSTUDIO_API_URL", "http://localhost:1234/v1/chat/completions")
LMSTUDIO_MODEL = os.getenv("SIA_LMSTUDIO_MODEL", "TheBloke/CodeLlama-34B-Python-GGUF")

# API authentication
SIA_API_KEY = os.getenv("SIA_API_KEY", "changeme")  # Set this in your environment for production

# Encryption key for memory encryption (Fernet key, base64-encoded)
SIA_ENCRYPTION_KEY = os.getenv("SIA_ENCRYPTION_KEY", None)