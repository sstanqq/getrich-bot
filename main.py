import os 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

import config

from time import sleep

from utils import add_proxy, get_random_useragent, get_accs, load_user_agent

def register_proxy(acc_name):
    PROXY_HOST = input('Host >> ')
    PROXY_PORT = input('Port >> ')
    PROXY_USER = input('Login >> ')
    PROXY_PASS = input('Password >> ')

    add_proxy(acc_name, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

# Create ness dirs
def create_dirs(): 
    for dir in [config.PROXIES_PATH, config.COOKIES_PATH, config.USERAGENTS_PATH]:
        if not os.path.exists(dir):
            os.makedirs(dir)


def main(acc_name):
    # Create ness dirs 
    # create_dirs()
    # cookies = get_accs(config.COOKIES_PATTERN, config.COOKIES_PATH)
    proxies = get_accs(config.PROXIES_PATTERN, config.PROXIES_PATH)
    user_agents = get_accs(config.USERAGENT_PATTERN, config.USERAGENTS_PATH)

    # Config Chrome 
    options = Options()
    options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    options.add_argument('--log-level=3')
    options.add_argument("--disable-infobars")


    if acc_name in user_agents:
        user_agent = load_user_agent(acc_name)
        options.add_argument(f"user-agent={user_agent}")
        print(f'[ INFO ] {acc_name}\'s user-agent connected successfully')
    if acc_name in proxies:
        options.add_extension(f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_PATTERN}')
        print(f'[ INFO ] {acc_name}\'s proxy connected successfully\n')

    service = Service(config.CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options )
    driver.implicitly_wait(60)

    driver.get('https://2ip.ru/')

    a = input('Продолжить ')

    driver.quit()

if __name__ == '__main__':
    # main()
    # register_proxy('cyanistan')
    # get_random_useragent('cyanistan')
    main('cyanistan')