import requests
from bs4 import BeautifulSoup
import re
import os
import sys
sys.path.append('db')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import local_db as db
import local_secrets as secrets
from logger import Logger

"""
TO DO

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
        and not link_url.lower().endswith(".atom") \
        and link_url != '/' \
        and link_url != initial_url + '/' \
        and link_url not in visited_urls \
        and initial_url + link_url not in visited_urls:
        return True
    else:
        return False

def get_page_contents(soup):
    page_text = ""

    for tag in soup(['script']):
        tag.decompose()

    print("checking class=body-container-wrapper")
    contents = soup.find(class_='body-container-wrapper')
    if contents == None:
        print("checking main")        
        contents = soup.find('main')
    if contents == None:
        print("checking class")
        contents = soup.find(class_='main-content-wrapper')
    if contents == None:
        print("checking id")
        contents = soup.find(id='content')
    if contents is not None:
        print("  contents found")  
        for content in contents:
            page_text = page_text + content.get_text("\n")
    else:
        print("getting all text from soup")
        page_text = soup.get_text("\n")
    page_text = page_text.encode(encoding='ASCII',errors='ignore').decode()
    #page_text = re.sub('\s+', ' ', page_text)

    return page_text

# Define a function to make a request and spider the website recursively
def spider(url, single):
    if url.lower().startswith('/www'):
        logger.log("***" + url)

    if len(url) > 250:
        print("url exceeded max length", url)
        logger.log(("url exceeded max length:\n" + url))
        return

    visited_urls.add(url)
    print(url, len(visited_urls))

    # Retrieve url into soup object
    try:
        response = requests.get(url, headers={"User-Agent": "XY"})
    except Exception as e:
        print ("Error retrieving url", url)
        logger.log("Error retrieving url:\n" +  str(e))
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract page text
    page_text = get_page_contents(soup)

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
                #print("parent", url)
                #print("link", link_url)
                spider(link_url, single)

def write_text_to_db(uri, text):
    print("saving: ", uri)
    #text = re.sub('\s+', ' ', text)
    if not db.insert_document(conn, domain_id, uri, "", text):
        print("*********************************")
        print("DB ERROR")
        logger.log("DB ERROR: " + uri)
    #print(text)
    return    

def write_text_to_file(uri, page_text):
    print("writing", uri)
    with open(file_name, "w") as file:
        file.writelines(uri + "\n\n")
        file.writelines(page_text + "\n\n")

# configure job
domain_id = 18
initial_url ='https://www.tvisioninsights.com'
single = False
file_name = "page.txt"

# init
visited_urls = set()
conn = db.get_connection()
logger = Logger()

# do it
spider(initial_url, single)

# cleanup
db.close_connection(conn)
print("------------------------")
print("set: ", visited_urls)
logger.log("DONE")
for url in visited_urls:
    logger.log(url)

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
