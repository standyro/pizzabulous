from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route('/')
def root():
    reviews = scrape_yelp(10)
    return render_template('index.jinja', reviews=reviews)

def scrape_yelp(results):
    html = requests.get('https://www.yelp.com/search?find_desc=Pizza&find_loc=New+York,+NY&start=' + str(results))
    # print(html.text)
    soup = BeautifulSoup(html.text, 'html.parser')
    results = soup.find_all('li', {"class": "regular-search-result"})
    yelp_reviews = []
    for result in results:
        if str(result) is not None:
            result_parsed = BeautifulSoup(str(result), 'html.parser')
            p = re.compile('(\d+\.\d+) star rating')
            rating = p.match(result_parsed.find('div', {"class": "i-stars"})['title'])
            rating_float = float(rating.group(1))
            yelp_reviews.append({
                'name': result_parsed.find('a', {"class": "biz-name"}).find('span').contents[0],
                'rating': int(rating_float)
            })
    return yelp_reviews

if __name__ == '__main__':
    app.run()
