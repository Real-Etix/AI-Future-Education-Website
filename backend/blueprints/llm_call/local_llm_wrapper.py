# backend/blueprints/llm_call/local_llm_wrapper.py

from llama_cpp import Llama
from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
from huggingface_hub import hf_hub_download
import multiprocessing
# import opencc
import asyncio

# startConverter = opencc.OpenCC('t2s.json')
# endConverter = opencc.OpenCC('s2hk.json')

class LocalLLM():
    def __init__(self, model_path, n_ctx=1024, draft_model=None):
        self.model_path = model_path
        self.draft_model = draft_model
        self.n_ctx = n_ctx
        self.llm = None
        print('Initialize LLM with init_llm() method.')

    def init_llm(self, verbose=False):
        print('Initializing LLM...')
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx = self.n_ctx,
            n_threads = multiprocessing.cpu_count(),
            draft_model = self.draft_model,
            verbose = verbose
        )
        print('Completed LLM initialization.')

    async def local_llm_completion(self, prompt, temperature=0.0, max_tokens=1024, stream=False):
        '''
        Send message to and receive response from LLM locally upon completion. 
        '''
        generation_kwargs = {
            "max_tokens": max_tokens,
            "stop": ['<|eot_id|>','<|end_of_text|>'],
            'temperature': temperature,
            'stream': stream
        }
        if not self.llm:
            yield "沒有"
        else:
            if stream:
                for chunk in self.llm.create_completion(prompt, **generation_kwargs):
                    text = chunk['choices'][0]['text'] # type: ignore
                    yield text
            else:
                response = self.llm.create_completion(prompt, **generation_kwargs)
                response_text = response['choices'][0]['text'] # type: ignore
                yield response_text 

    async def local_llm_response_stream(self, prompt):
        async for text in self.local_llm_completion(prompt, max_tokens=250, stream=True, temperature=0.8):
            print(text, end='', flush=True)
        print()  # Ensure a newline at the end





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    model_name = "hfl/Llama-3-Chinese-8B-Instruct-v3-GGUF"
    # model_name = "shenzhi-wang/Llama3-8B-Chinese-Chat-GGUF-8bit"
    filename = "ggml-model-q6_k.gguf"
    # filename = "Llama3-8B-Chinese-Chat-q8_0-v2_1.gguf" # Performance worse and slower
    model_path = hf_hub_download(model_name, filename=filename, local_dir='backend/model')
    llm1 = LocalLLM(model_path)
    llm1.init_llm()
    llm2 = LocalLLM(model_path)
    llm2.init_llm()
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
#故事要二百字內
        prompt2 = f'''<|start_header_id|>user<|end_header_id|>
        
創造二百字內的短故事，關於承諾，不用說故事告訴我們什麼。

例子："""
故事：{test_story[i]}
"""<|eot_id|><|start_header_id|>assistant<|end_header_id|>

故事：'''
        asyncio.run(llm1.local_llm_response_stream(prompt2))
        # text = asyncio.run(collect_response(response))
        # print(test_random_message[i], '->', response)
        # response = asyncio.run(llm2.local_llm_completion(prompt2, temperature=0.8, max_tokens = 100))
        # text = asyncio.run(collect_response(response))
        # print(test_random_message[i], '->', response)

