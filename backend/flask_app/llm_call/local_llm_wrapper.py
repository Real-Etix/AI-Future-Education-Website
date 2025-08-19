# backend/flask_app/llm_call/local_llm_wrapper.py

import llama_cpp
from huggingface_hub import hf_hub_download
import multiprocessing
import opencc
import asyncio
import pickle

# startConverter = opencc.OpenCC('t2s.json')
converter = opencc.OpenCC('s2hk.json')

class LocalLLM():
    def __init__(self, model_path, n_ctx=1024, draft_model=None, state_dir='backend/model/prompt_cache/'):
        self.model_path = model_path
        self.draft_model = draft_model
        self.n_ctx = n_ctx
        self.llm = None
        self.cache = None
        self.state_dir = state_dir
        print('Initialize LLM with init_llm() method.')

    def init_llm(self, verbose=False):
        print('Initializing LLM...')
        self.llm = llama_cpp.Llama(
            model_path = self.model_path,
            n_ctx = self.n_ctx,
            n_threads = multiprocessing.cpu_count(),
            n_batch = 512,
            n_ubatch = 512,
            flash_attn = True,
            verbose = verbose,
            n_gpu_layers=0,
        )
        print('Completed LLM initialization.')

    async def local_llm_completion(self, prompt, max_tokens=1024, stream=False, temperature=0.0, top_k=10, top_p=0.95, min_p=0.05, state_file=None):
        '''
        Send message to and receive response from LLM locally upon completion. 
        '''
        generation_kwargs = {
            "max_tokens": max_tokens,
            "stop": ['<|eot_id|>','<|end_of_text|>'],
            'temperature': temperature,
            'stream': stream,
            'top_k': top_k,
            'top_p': top_p,
            'min_p': min_p
        }
        if not self.llm:
            yield "沒有"
        else:
            if state_file:
                try:
                    with open(self.state_dir + state_file, 'rb') as f:
                        state = pickle.load(f)
                        self.llm.load_state(state)
                except: pass
            if stream:
                for chunk in self.llm.create_completion(prompt, **generation_kwargs):
                    text = chunk['choices'][0]['text'] # type: ignore
                    text = converter.convert(text)
                    yield text
            else:
                response = self.llm.create_completion(prompt, **generation_kwargs)
                response_text = response['choices'][0]['text'] # type: ignore
                response_text = converter.convert(response_text)
                yield response_text
    
    async def local_llm_chat_completion(self, prompt, max_tokens=1024, stream=False, temperature=0.0, top_k=10, top_p=0.95, min_p=0.05, state_file=None):
        '''
        Send message to and receive response from LLM locally upon completion.
        '''
        generation_kwargs = {
            "max_tokens": max_tokens,
            "stop": ['<|eot_id|>','<|end_of_text|>'],
            'temperature': temperature,
            'stream': stream,
            'top_k': top_k,
            'top_p': top_p,
            'min_p': min_p
        }
        if not self.llm:
            yield "沒有"
        else: 
            if state_file:
                try:
                    with open(self.state_dir + state_file, 'rb') as f:
                        state = pickle.load(f)
                        self.llm.load_state(state)
                except: pass
            messages = [{'role': 'user', 'content': prompt}]
            if stream:
                for chunk in self.llm.create_chat_completion(messages, **generation_kwargs): # type: ignore
                    response_message = chunk['choices'][0]['delta'] # type: ignore
                    if 'content' not in response_message:
                      continue
                    text = response_message['content'] # type: ignore
                    yield text
            else:
                response = self.llm.create_chat_completion(messages, **generation_kwargs) # type: ignore
                response_text = response['choices'][0]['message']['content'] # type: ignore
                yield response_text

    async def local_llm_response_stream(self, prompt, max_tokens, stream, temperature=0.8, top_k=10, top_p=0.95, min_p=0.05):
        async for text in self.local_llm_completion(
            prompt, 
            max_tokens=max_tokens, 
            stream=stream, 
            temperature=temperature,
            top_k = top_k,
            top_p = top_p,
            min_p = min_p
        ):
            print(text, end='', flush=True)
        print()  # Ensure a newline at the end
    
    def create_state(self, prefix, file, max_tokens=1024, stream=False, temperature=0.0, top_k=10, top_p=0.95, min_p=0.05, state_file=None):
        if self.llm:
            self.llm.reset()
            try:
                with open(self.state_dir + file, 'rb') as f:
                    state = pickle.load(f)
                    self.llm.load_state(state)
            except: print('No state loaded from disk')
            finally:
                generation_kwargs = {
                    "max_tokens": max_tokens,
                    "stop": ['<|eot_id|>','<|end_of_text|>'],
                    'temperature': temperature,
                    'stream': stream,
                    'top_k': top_k,
                    'top_p': top_p,
                    'min_p': min_p
                }
                self.llm.create_completion(prefix, **generation_kwargs)
                with open(self.state_dir + file, 'wb') as f:
                    pickle.dump(self.llm.save_state(), f)





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    model_name = "hfl/Llama-3-Chinese-8B-Instruct-v3-GGUF"
    # model_name = "shenzhi-wang/Llama3-8B-Chinese-Chat-GGUF-8bit"
    filename = "ggml-model-q6_k.gguf"
    # filename = "Llama3-8B-Chinese-Chat-q8_0-v2_1.gguf" # Performance worse and slower
    model_path = hf_hub_download(model_name, filename=filename, local_dir='backend/model')
    # draft_model = LlamaPromptLookupDecoding()
    draft_model = None
    llm1 = LocalLLM(model_path, draft_model=draft_model)
    llm1.init_llm(True)
    # llm2 = LocalLLM(model_path)
    # llm2.init_llm()
    print('Number of cores:', multiprocessing.cpu_count())
    test_random_message = ['承諾', "諾言", "怎樣遵守說過的？", "嗯？", "Who are you?"]
    test_story = [''.join(["春秋時期，吳國貴族季札出使拜訪徐國。徐國國君在接待季札時，看到了他佩帶",
        "的寶劍，流露出喜愛之情。細心的季札看出徐國國君的心意，但作為吳國使節，他到",
        "各諸侯國拜訪時不能沒有寶劍作配飾，這是一種外交禮儀，他不能不遵守，有辱自己",
        "的使命。於是季札向他承諾，完成出使後，必定把寶劍送給徐國國君。\n",
        "過了一段時間，季札終於完成出使任務，回程時途經徐國，他想去拜訪徐國國君，",
        "以贈送寶劍，卻驚訝發現徐國國君已死。季札感到十分遺憾，萬分悲痛地來到徐國國",
        "君墓前祭奠。祭奠完畢，他解下身上的寶劍，把它掛在墓旁的樹上。這時，侍從疑惑",
        "地問，為甚麼徐國國君已死，季札仍要留下珍貴的寶劍呢？季札解釋，當時他已承諾",
        "給徐國國君贈劍，不能因為徐國國君已死，就違背自己的諾言。"]),
        ''.join(["曾子是孔子的學生，為人很有信用，說到做到。\n",
        "一天，曾子的妻子要到市集，兒子哭哭鬧鬧地嚷着要跟媽媽一起",
        "上街。曾子的妻子不想帶着兒子去，便哄他說：「乖孩子，你先回家",
        "吧！待我回來，馬上宰了那頭胖胖白白的豬，給你弄一頓好吃的。」",
        "孩子聽到有豬肉吃，就不再哭鬧了。\n",
        "過了不久，妻子從市集回來，看見曾子拿起刀來，果真準備手起",
        "刀落，宰了那頭豬。妻子馬上三步拼作兩步，衝上前去阻止曾子說：",
        "「我剛才不過是跟孩子開個玩笑罷了，不是真的要把豬殺掉！」這時",
        "曾子一臉嚴肅地說：「我們不能跟兒子開這樣的玩笑！小孩子不懂",
        "事，只會聽從父母的教導，模仿父母的言行。為人父母者，必須以身",
        "作則，答應孩子的事，就要想辦法做到。今天如果我們不殺豬，就是",
        "欺騙兒子，也就等如教他欺騙別人。做母親的欺騙兒子，兒子以後都",
        "不會再相信母親了。這種事絕不能開玩笑，更不是教育孩子的方法！」\n",
        "妻子聽了點點頭。曾子於是把豬殺了，烹煮給兒子吃。"])]
    for i in range(2):
#         prompt1 = f'''<|start_header_id|>user<|end_header_id|>
        
# 分類用戶的意圖，意圖一定是：承諾、問候、沒有
# 如果不清楚，回答"沒有"。

# 用戶：{test_random_message[i]}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

# 意圖：'''
        prompt2 = f'''<|start_header_id|>user<|end_header_id|>

以下面的故事為靈感，創作一段中文故事，故事限制二百字內，不包含歷史或愛情主題。確保敘述簡潔明瞭，專注於塑造獨特的角色、不同的情節和新穎的場景。不要以證明、結論式陳述或道德教訓的方式結束，主體盡量有關承諾。

範例：故事講述了春秋時期吳國貴族季札出使徐國的經歷。徐國國君對季札佩帶的寶劍表現出喜愛，季札出於外交禮儀承諾在完成使命後將寶劍贈予國君。然而，當季札回程時發現國君已去世，感到非常遺憾。他仍然選擇在國君的墓前祭奠，並將寶劍掛在樹上，以此履行自己的承諾，表現出對承諾的重視和對亡者的敬意。故事強調了誠信與忠誠的重要性。\
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

故事：'''
        asyncio.run(llm1.local_llm_response_stream(prompt2, 200, True, temperature=2.0, top_k=2, top_p=0.9, min_p=0.1))
        # text = asyncio.run(collect_response(response))
        # print(test_random_message[i], '->', response)
        # response = asyncio.run(llm2.local_llm_completion(prompt2, temperature=0.8, max_tokens = 100))
        # text = asyncio.run(collect_response(response))
        # print(test_random_message[i], '->', response)

