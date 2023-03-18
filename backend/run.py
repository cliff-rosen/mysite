from utils import chunks_service as cs

user_message = 'What is the intervention trial number?'
#context_for_prompt = cs.get_context_for_prompt(chunks, 8000)
#context_for_prompt = context_for_prompt.encode(encoding='ASCII',errors='ignore').decode()

res = []

for i in range(10):
    print(i)