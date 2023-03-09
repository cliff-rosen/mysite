import requests
from bs4 import BeautifulSoup
import logging
import re
import os
import sys
sys.path.append('.\..')
from db import local_db as db
import json
import local_secrets as secrets


"""
TO DO
handle urls that have #
track status of visited urls (i.e. success, error)
Error retrieving url: maximum recursion depth exceeded
filter out feeds

need system to filter out garbage contents
"""

MAX_URL_LENGTH = 250
LOG_LEVEL = logging.INFO

logging.basicConfig(format='%(asctime)s  %(levelname)s - %(message)s', level=LOG_LEVEL, filename='spider.log', filemode='w')
logger = logging.getLogger()

def link_is_good(link_url):
    if link_url is None or link_url == "":
        return False
    if not link_url.lower().startswith(initial_url):
        return False
    if not link_url.lower().startswith("https"):
        return False
    if link_url in urls_seen:
        return False
    if len(url) > MAX_URL_LENGTH:
        print("url exceeded max length", url)
        return False

    # work around for Exemplar
    if domain_id == 22 \
        and (link_url.find('/blog/') > -1
            or link_url.find('/astro') > -1
            or link_url.find('/capital-deals/') > -1
            or link_url.find('/get-real/') > -1
            or link_url.find('/press-release/') > -1
            or link_url.find('/past-events/') > -1) \
        and link_url.find('/page/') > -1:
        print('--------------------------------------------')
        print('REDUNDANT LINK - REJECTING: ', link_url)
        return False

    if link_url.startswith("#") \
        or link_url.lower().find("mailto:") > -1 \
        or link_url.lower().find("tel:") > -1 \
        or link_url.lower().find("javascript:") > -1 \
        or link_url.lower().endswith(".jpg") \
        or link_url.lower().endswith(".jpeg") \
        or link_url.lower().endswith(".bmp") \
        or link_url.lower().endswith(".png") \
        or link_url.lower().endswith(".pdf") \
        or link_url.lower().endswith(".pptx") \
        or link_url.lower().endswith(".atom"):
        return False

    return True

def clean_url(link_url):
    if link_url is None or link_url == "" or link_url == '#' or link_url == '/':
        return link_url

    if link_url == initial_url + '/' or link_url == initial_url + '#':
        return initial_url

    pos = link_url.find('#')
    if pos > -1:
        link_url = link_url[:pos]

    if link_url.startswith("//"):
        return 'https:' + link_url

    if not link_url.startswith("http"):
        if not link_url.startswith("/"):
            link_url = '/' + link_url
        link_url = initial_url + link_url
    return link_url

def write_text_to_db(uri, text):
    print("-> saving: ", uri)
    if not db.insert_document(conn, domain_id, uri, "", text):
        logger.info("DB ERROR: " + uri)
    return    

def write_text_to_file(uri, page_text):
    print("writing", uri)
    with open(file_name, "w") as file:
        file.writelines(uri + "\n\n")
        file.writelines(page_text + "\n\n")

# Define a function to make a request and spider the website recursively
def spider(url, single):

    print("-> retrieving", len(urls_seen), url)

    # Retrieve url into soup object
    try:
        response = requests.get(url, headers={"User-Agent": "XY"})
    except Exception as e:
        print ("Error retrieving url", url)
        urls_seen[url]['status'] = 'ERROR'
        urls_seen[url]['detail'] = str(e)
        logger.info("Error retrieving url:\n" + "url\n" + str(e))
        return
    urls_seen[url]['status'] = 'RETRIEVED'

    # Extract page text
    soup = BeautifulSoup(response.content, 'html.parser')
    page_text = get_page_contents(soup)

    # Save page text
    if single == False:
        write_text_to_db(url, page_text)
    else:
        write_text_to_file(url, page_text)

    urls_seen[url]['status'] = 'COMPLETE'

    # Extract all the links on the page
    if single == False:
        links = soup.find_all('a')
        for link in links:
            link_url = clean_url(link.get('href'))
            if link_is_good(link_url):
                urls_to_visit.add(link_url)
                urls_seen[link_url] = {'status': 'PENDING'}

def get_page_contents(soup):
    page_text = ""
    contents = None
    for tag in soup(['script']):
        tag.decompose()

    if contents == None:
        print("checking id=main-content")
        contents = soup.find(id='main-content')
    if contents == None:
        print("checking id=MainContent")
        contents = soup.find(id='MainContent')
    if contents == None:
        print("checking class=main-content-wrapper")
        contents = soup.find(class_='main-content-wrapper')
    if contents == None:
        print("checking main")        
        contents = soup.find('main')
    if contents is not None:
        print("  contents found")  
        for content in contents:
            page_text = page_text + content.get_text("\n")
    else:
        print("getting all text from soup")
        page_text = soup.get_text("\n")
    page_text = page_text.encode(encoding='ASCII',errors='ignore').decode()
    #while bool(re.search(r'\s{3,}', page_text)):
    #    page_text = re.sub(r'\s{3,}', '\n\n', page_text)
    page_text = re.sub('\s{3,}', '\n\n', page_text)    

    return page_text

# configure job
file_name = "page.txt"
domain_id = 31
initial_url = 'https://karrikinsgroup.com'
single = False

# init
urls_to_visit = set()
urls_seen = {}
conn = db.get_connection()
logger.info("Starting spider for " + initial_url)

# do it
urls_to_visit.add(initial_url)
urls_seen[initial_url] = {'status': 'PENDING'}
while(urls_to_visit):
    print("-------------------------------------")
    print("REMAINING: ", len(urls_to_visit))
    url = urls_to_visit.pop()
    spider(url, single)

# cleanup
db.close_connection(conn)
print("------------------------")
print("URLs seen:\n", urls_seen)
logger.info("DONE")
for url in urls_seen:
    logger.info(url + ': ' + json.dumps(urls_seen[url]))

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
