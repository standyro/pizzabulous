import unittest
import pizzabulous

class TestPizzabulous(unittest.TestCase):
    def test_scrape_yelp(self):
        scraping_list = pizzabulous.scrape_yelp(10)
        self.assertEqual(len(scraping_list), 10)

if __name__ == '__main__':
    unittest.main()
