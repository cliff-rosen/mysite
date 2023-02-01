import requests
from bs4 import BeautifulSoup
import re
import sys
sys.path.append('db')
import local_db as db

"""
TO DO
    exclusions other than .jpg
    isolate text within page worth saving
"""

# Define a function to make a request and spider the website recursively
def spider(url):
    response = requests.get(url, headers={"User-Agent": "XY"})
    soup = BeautifulSoup(response.content, 'html.parser')
    visited_urls.add(url)

    # Extract page text and save it to db
    page_text = ""
    for main in soup.find_all('main'):
        page_text = page_text + main.get_text()
    save_text(url, page_text)

    # Extract all the links on the page
    links = soup.find_all('a')
    for link in links:
        link_url = link.get('href')

        # Check if the link is a valid URL and has not been visited yet
        if link_url is not None \
            and link_url.startswith(initial_url) \
            and not link_url.endswith(".jpg") \
            and link_url not in visited_urls:
            print(link_url)
            spider(link_url)
        #else:
            #print("rejected: ", link_url)

def save_text(uri, text):
    print("saving: ", uri)
    #text = re.sub('\s+', ' ', text)
    db.insert_document(conn, domain_id, uri, "", text)
    #print(text)
    return    

def run_spider():
    conn = db.get_connection()
    spider(initial_url)
    db.close_connection(conn)
    print("------------------------")
    print("set: ", visited_urls)

def count_links(url):
    response = requests.get(url, headers={"User-Agent": "XY"})
    soup = BeautifulSoup(response.content, 'html.parser')
    visited_urls.add(url)

    # Extract all the links on the page
    links = soup.find_all('a')
    for link in links:
        link_url = link.get('href')

        # Check if the link is a valid URL and has not been visited yet
        if link_url is not None \
            and link_url.startswith(initial_url) \
            and not link_url.endswith(".jpg") \
            and not link_url.endswith(".pdf") \
            and link_url not in visited_urls:
            print(link_url)
            spider(link_url)
        #else:
            #print("rejected: ", link_url)

# configuration values
domain_id = 2
initial_url = 'https://everplans.com'

# process initial url
visited_urls = set()

count_links(initial_url)
print("visited urls", visited_urls)
print("visited url count", len(visited_urls))

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