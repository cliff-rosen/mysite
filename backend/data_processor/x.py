import re

filepath = "page.txt"

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def write_file(filepath, text):
    with open(filepath, 'w', encoding='utf-8') as outfile:
         outfile.write(text + '\n')

text = read_file(filepath)

text1 = text
while text1.find("\n\n\n") > -1:
    text1 = text1.replace("\n\n\n", "\n\n")
write_file('page1.txt', text1)

text2 = text
while bool(re.search(r'\s{3,}', text2)):
    text2 = re.sub(r'\s{3,}', '\n', text2)
write_file('page2.txt', text2)
