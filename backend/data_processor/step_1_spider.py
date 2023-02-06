import requests
from bs4 import BeautifulSoup
import re
import os
import sys
sys.path.append('db')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets

"""
TO DO
    exclusions other than .jpg
    isolate text within page worth saving
"""

def link_is_good(link_url):
    if link_url is not None \
        and (link_url.startswith(initial_url) or not link_url.startswith("http"))\
        and not link_url.startswith("#") \
        and not link_url.lower().startswith("mailto:") \
        and not link_url.lower().startswith("tel:") \
        and not link_url.lower().startswith("javascript:") \
        and not link_url.lower().endswith(".jpg") \
        and not link_url.lower().endswith(".pdf") \
        and link_url != '/' \
        and link_url != initial_url + '/' \
        and link_url not in visited_urls \
        and initial_url + link_url not in visited_urls:
        return True
    else:
        return False        

# Define a function to make a request and spider the website recursively
def spider(url, single):
    visited_urls.add(url)
    print(url, len(visited_urls))

    # Retrieve url into soup object
    try:
        response = requests.get(url, headers={"User-Agent": "XY"})
    except Exception as e:
        print ("Error retrieving url", url)
        print("----- ERROR -----")
        print(e)
        print("--------------")
        return
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract page text
    page_text = ""
    #for main in soup.find_all('main'):
    contents = soup.find(id='content')
    if contents is not None:
        for content in contents:
            page_text = page_text + content.get_text("\n")
    if page_text == "":
        page_text = soup.get_text("\n")

    # Clean page text
    page_text = page_text.encode(encoding='ASCII',errors='ignore').decode()
    #page_text = re.sub('\s+', ' ', page_text)

    # Save page text
    if single == False:
        write_text_to_db(url, page_text)
    else:
        write_text_to_file(url, page_text)

    # Extract all the links on the page
    if single == False:
        links = soup.find_all('a')
        for link in links:
            link_url = link.get('href')
            if link_is_good(link_url):
                if not link_url.startswith("http"):
                    link_url = initial_url + link_url
                spider(link_url, single)

def write_text_to_db(uri, text):
    print("saving: ", uri)
    #text = re.sub('\s+', ' ', text)
    db.insert_document(conn, domain_id, uri, "", text)
    #print(text)
    return    

def write_text_to_file(uri, page_text):
    with open(file_name, "a") as file:
        file.writelines(uri + "\n\n")
        file.writelines(page_text + "\n\n")

# configure job
domain_id = 10
initial_url = "http://www.pureti.com"
#initial_url = "https://www.pureti.com/benefits/"
single = False
file_name = "page.txt"

# init
visited_urls = set()
conn = db.get_connection()

# do it
spider(initial_url, single)

# cleanup
db.close_connection(conn)
print("------------------------")
print("set: ", visited_urls)


"""
filter out pdfs but find another way to harvest them
ignore uploads folder?
delete:
 documents
  pdf documents
  empty text
 document_chunk
  chunks that are just whitespace
"""
