from db import local_db as db

def get_conversation_history(conversation_id):
    conversation_text = ""
    user = 'Patient'
    ai = 'Chatbot'
    rows = db.get_conversation_history(conversation_id)
    for row in rows:
        conversation_text += f"{user}: {row['query_text']}\n{ai}: {row['response_text']}\n\n"
    return conversation_text


conversation_id = 'oreWdVptvFMR8HVqiVgW'
print(get_conversation_history(conversation_id))