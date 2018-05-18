import unittest
import pizzabulous

class TestPizzabulous(unittest.TestCase):
    def test_get_reviews(self):
        scraping_list = pizzabulous.scrape_yelp(10)
        for review in scraping_list:
            self.assertIn('name', review)
            self.assertIn('rating', review)
        self.assertEqual(len(scraping_list), 10)

if __name__ == '__main__':
    unittest.main()
