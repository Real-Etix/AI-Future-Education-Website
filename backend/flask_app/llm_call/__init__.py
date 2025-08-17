# backend/flask_app/llm_call/__init__.py

from .local_llm_wrapper import LocalLLM
from .scenario_similarity import RetrievalModel
from .llm_wrapper import client, llm_response
from huggingface_hub import hf_hub_download

model_name = "hfl/Llama-3-Chinese-8B-Instruct-v3-GGUF"
model_file = "ggml-model-q6_k.gguf"
model_path = hf_hub_download(model_name, filename=model_file, local_dir='backend/model')
# model_path = "Removed for testing purposes"

state_dir = 'backend/model/prompt_cache/'
local_llm = LocalLLM(model_path, n_ctx=1024, state_dir='backend/model/prompt_cache/')

model_name = 'DMetaSoul/sbert-chinese-general-v2'
model_path = 'backend/model/sentence_encoder'
csv_path = 'backend/database/scenario.csv'
index_path = 'backend/database/scenario.index'
retrieval_llm = RetrievalModel(model_name, model_path, csv_path, index_path)