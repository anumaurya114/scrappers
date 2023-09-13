import unittest
from crawler import Crawler


    
class CrawlerBasicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.crawler = Crawler()
    
    def test_webpageOpeningTest(self) -> None:
        pageUrl = "https://www.python.org"
        
        page = self.crawler.getPage(pageUrl)
        pageSource = page.page_source
        title = page.title
        correctTitle = "Welcome to python.org"
        isHtml = pageSource.startswith("<html")

        self.assertEqual(title.lower(), correctTitle.lower())
        self.assertEqual(isHtml, True)
    
def getSuite():
    suite = unittest.TestSuite()
    suite.addTest(CrawlerBasicTests('test_webpageOpeningTest'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(getSuite())
    input()