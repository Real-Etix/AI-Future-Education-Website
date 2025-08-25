import requests
import json
import time

prompt = '''受以下故事為靈感，寫一篇不超過二百字的中文故事，不要涉及歷史、犯罪、鬥爭或愛情。敘事要簡潔明瞭，聚焦在獨特的人物、豐富的情節和新穎的場景，避免以勸告、結論或道德教訓的方式結束。主體必須有關實行承諾。

靈感：在春秋時期，吳國貴族季札出使徐國，因徐國國君喜愛他的寶劍，季札承諾在完成任務後贈送寶劍。然而，當季札回程時發現徐國國君已死，感到悲痛，於是前往墓前祭奠，並將寶劍掛在樹上以履行自己的承諾，表現了他對信義的堅持。

故事：'''
max_tokens=500
temperature=0.8
top_k=0
top_p=1.0
min_p=0.1
stream = True
num_char = 0

def get_stream(url):
    global num_char
    s = requests.Session()

    with s.post(url, json={
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "min_p": min_p,
        "stream": stream
    }, stream=True, timeout=600) as resp:
        for line in resp.iter_lines(chunk_size=16):
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[len("data: "):]
                    try:
                        data_json = json.loads(data_str)
                        text = data_json.get('text', '')
                        status = data_json.get('status', '')
                        if status == 'stream':
                            print(text, end='', flush=True)
                            num_char += len(text)
                        elif status == 'start':
                            print("\n[Stream started]\n", flush=True)
                        elif status == 'end':
                            print("\n[Stream ended]\n", flush=True)
                    except json.JSONDecodeError:
                        print(f"\n[Error decoding JSON: {data_str}]\n", flush=True)

url = 'http://ec2-13-251-104-194.ap-southeast-1.compute.amazonaws.com/respond'
start_time = time.time()
get_stream(url)
print(f'\nTotal characters: {num_char}')
print(f'Time taken: {time.time() - start_time} seconds')