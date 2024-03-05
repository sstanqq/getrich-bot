import os 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import config

def create_dirs():
    # Create ness dirs 
    for dir in [config.PROXIES_PATH, config.COOKIES_PATH, config.USERAGENTS_PATH]:
        if not os.path.exists(dir):
            os.makedirs(dir)

def main():
    create_dirs()

if __name__ == '__main__':
    main()