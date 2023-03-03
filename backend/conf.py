

DEFAULT_INITIAL_PROMPT = """
You are a chatbot working as a customer service representative for a company.
The following question is from a potential customer.
Answer the question as truthfully as possible.  
Use only the provided context and no further information to answer the question.
If you are not certain of the answer, say "I don't know."\n\n
"""

DEFAULT_INITIAL_MESSAGE = "Hello, how can I help you?"

DEFAULT_FOLLOWUP_PROMPT = """
Context:###\n<<CONTEXT>>\n###\n
Question: <<QUESTION>>\n
Answer: 
"""

"""
prompt built from:
    initial_prompt
    conversation_history
    followup_prompt

initial_prompt comes from domain || default
        
conversation_history built from get_conversation_history()

followup_prompt build from followup_prompt_template
    followup_prompt_template comes from domain || default
    if contains <<CONTEXT>>, context retrieved via Pinecone

-----

get_answer(
    model, 
    conversation_id,
    prompt,
    query
    use_context
    )

prompt built from:
    initial_prompt
    optional context
    conversation_history
    new question

openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
)    
    
"""