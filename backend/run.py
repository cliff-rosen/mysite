from db import local_db as db

conversation_id = 'kqtKAjrekaN1SqZSH3lM'
res = db.get_conversation(conversation_id)[0]['conversation_text']
print(res)

#db.update_conversation(conversation_id, 'hello')
