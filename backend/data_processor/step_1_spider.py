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

def link_is_good(link_url):
    if link_url is not None \
        and (link_url.startswith(initial_url) or not link_url.startswith("http"))\
        and not link_url.startswith("#") \
        and not link_url.startswith("mailto:") \
        and not link_url.endswith(".jpg") \
        and not link_url.endswith(".pdf") \
        and link_url != '/' \
        and link_url != initial_url + '/' \
        and link_url not in visited_urls \
        and initial_url + link_url not in visited_urls:
        return True
    else:
        return False        

# Define a function to make a request and spider the website recursively
def spider(url):
    visited_urls.add(url)
    print(url, len(visited_urls))
    response = requests.get(url, headers={"User-Agent": "XY"})
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract page text and save it to db
    page_text = ""
    for main in soup.find_all('main'):
        page_text = page_text + main.get_text("\n") + "\n\n-----\n\n"

    write_text_to_db(url, page_text)
    #write_text_to_file(url, page_text)

    # Extract all the links on the page
    links = soup.find_all('a')
    for link in links:
        link_url = link.get('href')
        if link_is_good(link_url):
            if not link_url.startswith("http"):
                link_url = initial_url + link_url
            spider(link_url)
        #else:
        #    print("rejected: ", link_url)

def write_text_to_db(uri, text):
    print("saving: ", uri)
    #text = re.sub('\s+', ' ', text)
    db.insert_document(conn, domain_id, uri, "", text)
    #print(text)
    return    

def write_text_to_file(uri, page_text):
    with open(file_name, "a") as file:
        file.writelines(uri + "\n\n")
        #file.writelines(page_text + "\n\n")
        file.writelines(page_text.encode(encoding='ASCII',errors='ignore').decode() + "\n\n")
        #file.writelines(re.sub('\s+', ' ', page_text) + "\n\n")


# configure job
domain_id = 3
initial_url = 'https://everplans.com'
#initial_url = 'https://www.everplans.com/health-organization'
#initial_url = 'https://www.everplans.com/topics'
file_name = "page.txt"

# init
visited_urls = set()
conn = db.get_connection()

# do it
spider(initial_url)

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
