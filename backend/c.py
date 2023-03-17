c_str = 'C'

def set(i):
    global c_str
    c_str = i

def get():
    return c_str

print('c_str=%s' % c_str)
