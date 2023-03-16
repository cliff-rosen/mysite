import tiktoken

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)

    num_tokens = len(encoding.encode(string))
    return num_tokens

s = '''
this is the string i want to tokenize
'''
model = 'text-davinci-003'

n = num_tokens_from_string(s, model)
print(n)
