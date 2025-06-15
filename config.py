import os
from dotenv import load_dotenv

load_dotenv()

# Ollama config for AutoGen with thinking disabled
# OLLAMA_THINKING_CONFIG = {
#     "config_list": [{
#         "model": os.getenv("OLLAMA_MODEL", "qwen3:8b"),
#         "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1",
#         "api_key": "ollama",  # Required but not used
#         "extra_body": {
#             "think": False  # Disable thinking mode
#         }
#     }],
#     "cache_seed": None,  # No caching for testing
# }

OLLAMA_VL_CONFIG = {
    "config_list": [{
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5vl:3b"),
        "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/v1",
        "api_key": "ollama",  # Required but not used
        "extra_body": {
            "think": False  # Disable thinking mode
        }
    }],
    "cache_seed": None,  # No caching for testing
}