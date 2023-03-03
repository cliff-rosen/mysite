

DEFAULT_INITIAL_PROMPT = """
You are a chatbot working as a customer service representative for a company.
The following question is from a potential customer.
Answer the question as truthfully as possible.  
Use only the provided context and no further information to answer the question.
If you are not certain of the answer, say "I don't know."\n\n
"""

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
    if contains <<CONTEXT>>, context retrieved from pinecone
    
"""