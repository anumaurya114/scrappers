from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import time

__all__ = [
    "Crawler",
    "CrawlerBuilder",
]

class Crawler:
    def __init__(self, executable_path="./chromedriver", defaultPause=5, headLess=True) -> None:
        """
        defaultPause: page on each url access, pause time in seconds
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode

        # Optional: You can also set other preferences or disable images to improve performance
        chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
        chrome_options.add_argument("--no-sandbox")  # Disable sandbox for headless mode
        chrome_options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage for headless mode
        if headLess:
            self.driver = Chrome(executable_path=executable_path, chrome_options=chrome_options)
        else:
            self.driver = Chrome(executable_path=executable_path)
        self.defaultPause = defaultPause

    def getPage(self, url, pause=0.2):
        self.driver.get(url)
        self.pause(pause)
        return self.driver
    
    def pause(self, pause=5):
        time.sleep(pause)
    
    def getDriver(self):
        return self.driver 

    @property
    def page_source(self):
        return self.driver.page_source

class CrawlerBuilder:
    def getCrawler():
        return Crawler()
