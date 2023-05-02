
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

df = pd.read_csv('dataset_google-search-scraper_2023-04-30_21-21-04-757.csv')

cols = []
for i in df.columns:
    if 'url' in i and 'organicResults' in i:
        cols.append(i)
    if 'searchQuery/term' in i: 
        cols.insert(0, i)
urls = df[cols]
urls = urls.melt(id_vars=['searchQuery/term'], var_name='result_num', value_name='url').dropna()


all = []
issues = []
for i, url in enumerate(tqdm(urls['url'][1:])):
    if i > 1: break
    # Get the HTML content from the URL
    try: 
        response = requests.get(url, timeout=10)
        html_content = response.content

        # Use Beautiful Soup to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all headers and the text underneath them
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    except Exception as e:
        issues.append((response.status_code, response.text, e))
        headers = []

    all_headers = []
    all_texts = []
    for header in tqdm(headers, total=len(headers), leave=False):
        if isinstance(header, str):
            header_text = header
            next_elems = []
        else:
            header_text = header.get_text()
            next_elems = header.find_next_siblings()
        # Find the next element(s) after the header
        
        text = ''
        for elem in next_elems:
            # Stop when we reach another header
            if elem.name.startswith('h'):
                break
            else:
                text += elem.get_text()
        all_texts.append(text)
        all_headers.append(header)
    all.append({'url': url, 'headers': all_headers, 'text': all_texts})
print(all)
import pickle
with open('all_scraped.pkl', 'wb') as f:
    pickle.dump(all, f)

with open('issues.pkl', 'wb') as f:
    pickle.dump(issues, f)