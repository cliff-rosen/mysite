import openai
import local_secrets as secrets
import logging

'''
gpt-4, gpt-4-0314, gpt-4-32k, gpt-4-32k-0314
'''

OPENAI_API_KEY = secrets.OPENAI_API_KEY
LOG_LEVEL = logging.INFO

logging.basicConfig(format='%(asctime)s  %(levelname)s - %(message)s', level=LOG_LEVEL, filename='app2.log', filemode='w')

openai.api_key = OPENAI_API_KEY
model = "gpt-3.5-turbo"
model = 'gpt-4'

completion = openai.ChatCompletion.create(
  model=model,
  messages=[
    {"role": "user", "content": "Why does graphics software use imaginary numbers?"}
  ]
)

print(completion.choices[0].message)

