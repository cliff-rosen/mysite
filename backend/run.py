from db import local_db as db


def f1():
    print('f1 says hello')
    f2()


def f2():
    print('f2 says hello')
    

f1()
