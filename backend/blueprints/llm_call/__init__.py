# backend/blueprints/llm_call/__init__.py

from .local_llm_wrapper import LocalLLM
from .llm_wrapper import client, llm_response
from huggingface_hub import hf_hub_download

model_name = "hfl/Llama-3-Chinese-8B-Instruct-v3-GGUF"
model_file = "ggml-model-q6_k.gguf"
# model_path = hf_hub_download(model_name, filename=model_file, local_dir='backend/model')
model_path = "Removed for testing purposes"

classify_llm = LocalLLM(model_path, n_ctx=512)
story_llm = LocalLLM(model_path, n_ctx=1024)