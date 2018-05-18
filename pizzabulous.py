from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, jsonify
import re
import itertools

app = Flask(__name__)


@app.route('/')
def root():
    num_of_reviews = int(request.args.get('reviews', 10))
    reviews = scrape_yelp(num_of_reviews)
    return render_template('index.jinja',
                           num_of_reviews=num_of_reviews,
                           reviews=reviews)
@app.route('/api')
def api():
    num_of_reviews = int(request.args.get('reviews', 10))
    reviews = scrape_yelp(num_of_reviews)
    return jsonify(reviews)


def scrape_yelp(num_of_reviews):
    if num_of_reviews < 10:
        total_reviews = get_reviews(num_of_reviews)
    else:
        total = list(range(0, num_of_reviews, 10))
        reviews = [get_reviews(number) for number in total]
        total_reviews = list(itertools.chain(*reviews))
    return total_reviews


def process_single_result(result):
    if str(result) is not None:
        result_parsed = BeautifulSoup(str(result), 'html.parser')
        p = re.compile('(\d+\.\d+) star rating') # strip
        rating_text = result_parsed.find('div', {'class': 'i-stars'})['title']
        rating = p.match(rating_text)
        rating_float = float(rating.group(1))
        business_html = result_parsed.find('a', {'class': 'biz-name'})
        name = business_html.find('span').contents[0]
        return {
            'name': name,
            'rating': int(rating_float)
        }

def get_reviews(offset):
    html = requests.get('https://www.yelp.com/search?find_desc=Pizza&find_loc=New+York,+NY&start=' + str(offset))
    soup = BeautifulSoup(html.text, 'html.parser')
    results = soup.find_all('li', {'class': 'regular-search-result'})
    yelp_reviews = [process_single_result(result) for result in results]
    return yelp_reviews


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
