# backend/blueprints/llm_call/local_llm_wrapper.py

from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import multiprocessing
# import opencc
import asyncio

# startConverter = opencc.OpenCC('t2s.json')
# endConverter = opencc.OpenCC('s2hk.json')

class LocalLLM():
    def __init__(self, model_path):
        self.model_path = model_path

    def init_llm(self):
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx = 512,
            n_threads = multiprocessing.cpu_count(),
            verbose = False
        )

    async def local_llm_response(self, prompt, temperature=0, max_tokens=1024):
        '''
        Send message to and receive response from LLM locally. 
        '''
        generation_kwargs = {
            "max_tokens": max_tokens,
            "stop": ['<|eot_id|>','<|end_of_text|>'],
            'temperature': temperature,
        }
        # prompt = startConverter.convert(prompt)
        response = self.llm.create_completion(prompt, **generation_kwargs)
        response_text = response['choices'][0]['text'] # type: ignore
        # translated_text = endConverter.convert(response_text)
        return response_text





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    model_name = "hfl/Llama-3-Chinese-8B-Instruct-v3-GGUF"
    model_file = "ggml-model-q6_k.gguf"
    print(1)
    model_path = hf_hub_download(model_name, filename=model_file, local_dir='backend/model')
    print(2)
    llm = LocalLLM(model_path)
    print(3)
    llm.init_llm()
    print(4)
    print('Number of cores:', multiprocessing.cpu_count())
    test_random_message = ['承諾', "諾言", "怎樣遵守說過的？", "嗯？", "Who are you?"]
    for i in range(5):
        prompt1 = f'''<|start_header_id|>user<|end_header_id|>
        
從回答分類用戶的意圖，意圖一定是：承諾、問候、沒有
如果不清楚，回答"沒有"。

例子："""
用戶：我想知道什麼是諾言。
意圖：承諾
用戶：你是誰？
意圖：問候
"""

用戶：{test_random_message[i]}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

意圖：'''
        print(test_random_message[i], '->', asyncio.run(llm.local_llm_response(prompt1, max_tokens=5)))