
rows = [(1, 2), (3,4)]

da = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]    
for d in da:
    print(d)
    for key in d.keys():
        print(key, d[key])