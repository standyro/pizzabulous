from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, jsonify
from urllib.parse import quote_plus, unquote
import re
import itertools
import json
import logging
from statistics import mean

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def root():
    num_of_reviews = int(request.args.get('reviews', 10))
    reviews = scrape_yelp(num_of_reviews)
    return render_template('index.jinja',
                           num_of_reviews=num_of_reviews,
                           reviews=reviews)
@app.route('/reviews')
def reviews():
    name = request.args.get('name')
    reviews_json = scrape_yelp_single_restaurant_reviews(name)
    log.debug(reviews_json)
    reviews = reviews_json.get('review')
    ratings = [review['reviewRating']['ratingValue'] for review in reviews]
    score = mean(ratings)
    name = reviews_json.get('name')
    return render_template('reviews.jinja',
                           name=name,
                           score=score,
                           reviews=reviews)

@app.route('/search')
def search():
    name = request.args.get('name')
    num_of_reviews = int(request.args.get('reviews', 10))
    total_reviews = get_reviews(0, name)
    reviews_json = scrape_yelp_single_restaurant_reviews(total_reviews[0]['href'])
    log.debug(reviews_json)
    reviews = reviews_json.get('review')[0:num_of_reviews]
    ratings = [review['reviewRating']['ratingValue'] for review in reviews]
    score = mean(ratings)
    name = reviews_json.get('name')
    return render_template('reviews.jinja',
                           name=name,
                           score=score,
                           reviews=reviews)

@app.route('/api')
def api():
    num_of_reviews = int(request.args.get('reviews', 10))
    reviews = scrape_yelp(num_of_reviews)
    return jsonify(reviews)


def scrape_yelp(num_of_reviews):
    if num_of_reviews < 10:
        total_reviews = get_reviews(num_of_reviews)[0:num_of_reviews]
        # yelp only returns 10 reviews, so discard the rest
    else:
        total = list(range(0, num_of_reviews, 10))
        reviews = [get_reviews(number) for number in total]
        total_reviews = list(itertools.chain(*reviews))
    return total_reviews

def scrape_yelp_single_restaurant_reviews(restaurant_name):
    html = requests.get('https://www.yelp.com/' + unquote(restaurant_name))
    soup = BeautifulSoup(html.text, 'html.parser')
    results = soup.find_all('script', {'type': 'application/ld+json'})[0].contents[0]
    results_json = json.loads(results)
    return results_json

def process_single_result(result):
    if str(result) is not None:
        result_parsed = BeautifulSoup(str(result), 'html.parser')
        p = re.compile('(\d+\.\d+) star rating') # strip from text
        rating_text = result_parsed.find('div', {'class': 'i-stars'})['title']
        rating = p.match(rating_text)
        rating_float = float(rating.group(1))
        business_html = result_parsed.find('a', {'class': 'biz-name'})
        href = result_parsed.find('a').attrs.get('href')
        name = business_html.find('span').contents[0]
        result_dict = {
            'name': name,
            'rating': int(rating_float),
            'href': quote_plus(href)
        }
        log.debug(result_dict)
        return result_dict


def get_reviews(offset, query=''):
    url = 'https://www.yelp.com/search?find_desc=' + query + '+pizza&find_loc=New+York,+NY&start=' + str(offset)
    log.debug(url)
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    results = soup.find_all('li', {'class': 'regular-search-result'})
    yelp_reviews = [process_single_result(result) for result in results]
    return yelp_reviews


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
