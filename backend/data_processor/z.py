import os
import re
from PyPDF2 import PdfReader

directory = 'outputs'
dest = 'pages.txt'

def write(text):
    with open(os.path.join(directory, dest), 'a') as new_file:
        new_file.write(text)

reader = PdfReader("inputs\protocol.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[1]

def visitor_body(text, cm, tm, font_dict, font_size):
    pattern = r'^\s*$'
    if bool(re.match(pattern, text)):
        return
    
    write(text.strip() + ' ' )

page.extract_text(visitor_text=visitor_body)


'''
for page in reader.pages:
    text = page.extract_text()
    #text = text.encode(encoding='ASCII',errors='ignore').decode()
    text = text.encode(encoding='ASCII',errors='ignore').decode()
    try:
        write(text)
    except Exception as e:
        print('Couldnt read page: ', str(e))
              
'''