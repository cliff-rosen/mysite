


prompt = """
You are a chatbot working as a customer service representative for a company.
The following question is from a potential customer.
Answer the question as truthfully as possible.  
Use only the provided context and no further information to answer the question.
If you are not certain of the answer, say "I don't know."\n\n
Context:\n<<<CONTEXT>>>\n\n 
Question:\n<<<QUESTION>>>\n\n
Answer:
"""
context = "abcde"
question = "defghi"

prompt = prompt.replace("<<CONTEXT>>", context)
prompt = prompt.replace("<<QUESTION>>", question)
print(prompt)


