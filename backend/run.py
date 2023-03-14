from db import local_db as db



chunks = {
    'a': {'x': 5, 'y': 7},
    'b': {'x': 8, 'y': 10}
}

items = chunks.items()
for item in items:
    print(item[1])