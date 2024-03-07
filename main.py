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
import json

import config

from time import sleep

from utils import add_proxy, get_random_useragent, get_accs, load_user_data, \
                  proxy_validator, load_txt_data, email_validator, save_user_data

import proxies

def register_proxy(acc_name, ref):
    PROXY_HOST = input('Host >> ')
    PROXY_PORT = input('Port >> ')
    PROXY_USER = input('Login >> ')
    PROXY_PASS = input('Password >> ')

    checker = proxy_validator(PROXY_HOST, PROXY_PORT)
    if not checker:
        print('[INFO] Введите корректный proxy')
        return False 

    checker = proxies.check_proxy(ref, PROXY_HOST)
    if not checker:
        print('[INFO] Такой proxy уже существует')
        return False 

    proxies.add_proxy(ref, PROXY_HOST, PROXY_PORT)
    add_proxy(acc_name, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    return True

# Create ness dirs
def create_dirs(): 
    for dir in [config.PROXIES_PATH, config.USERDATA_PATH, config.USERAGENTS_PATH]:
        if not os.path.exists(dir):
            os.makedirs(dir)

# Proxy checker
def proxy_checker(driver, acc_name):
    url = 'https://2ip.ru/'
    proxies_txt = get_accs(config.PROXIES_TXT_PATTERN, config.PROXIES_PATH)

    if acc_name in proxies_txt:
        acc_proxy = load_txt_data(acc_name, config.PROXIES_PATH, config.PROXIES_TXT_PATTERN)
    else:
        return False

    driver.get(url)

    try:
        wait = WebDriverWait(driver, 30)
        ip_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ip-info')))
    except TimeoutException:
        return False 
    
    ip_host = ip_div.find_element(By.TAG_NAME, 'span').text

    if ip_host != acc_proxy:
        return False 

    return True

def add_user_data(acc_name):
    email = input('\nEmail >> ')
    if not email_validator(email):
        print('[ERROR] Incorrect email')
        return False 
    password = input('Password >> ')
    save_user_data(acc_name, email.strip(), password.strip())
    print('[INFO] User data successfully saved')

def register_account(acc_name, ref):
    # Get New user-agent 
    get_random_useragent(acc_name)

    # Register new proxy
    flag = register_proxy(acc_name, ref)
    if not flag:
        print('[ERROR] Can\'t register a new proxy')
        return False 

    add_user_data(acc_name)

    proxies = get_accs(config.PROXIES_PATTERN, config.PROXIES_PATH)
    user_agents = get_accs(config.USERAGENT_PATTERN, config.USERAGENTS_PATH)

    # Config Chrome 
    options = Options()
    options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    options.add_argument('--log-level=3')
    options.add_argument("--disable-infobars")

    if acc_name in user_agents:
        user_agent = load_txt_data(acc_name, config.USERAGENTS_PATH, config.USERAGENT_PATTERN)
        options.add_argument(f"user-agent={user_agent}")
        print(f'[ INFO ] {acc_name}\'s user-agent connected successfully')
    else:
        return False
    if acc_name in proxies:
        options.add_extension(f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_PATTERN}')
        print(f'[ INFO ] {acc_name}\'s proxy connected successfully\n')
    else:
        return False

    service = Service(config.CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options )
    driver.implicitly_wait(60)

    flag = proxy_checker(driver, acc_name)
    if not flag:
        driver.quit()
        return False

    wait = WebDriverWait(driver, 30)

    reg_url = 'https://getrich.tv/register'
    driver.get(reg_url)
    text_inputs = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'input-text__input')))

    print(len(text_inputs))
    text_inputs[2].send_keys(acc_name)

    a = input('Продолжить(Enter) >>')

    driver.quit()

def register_cookies(acc_name):
    proxies = get_accs(config.PROXIES_PATTERN, config.PROXIES_PATH)
    user_agents = get_accs(config.USERAGENT_PATTERN, config.USERAGENTS_PATH)

    # Config Chrome 
    options = Options()
    options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    options.add_argument('--log-level=3')
    options.add_argument("--disable-infobars")

    if acc_name in user_agents:
        user_agent = load_txt_data(acc_name, config.USERAGENTS_PATH, config.USERAGENT_PATTERN)
        options.add_argument(f"user-agent={user_agent}")
        print(f'[ INFO ] {acc_name}\'s user-agent connected successfully')
    else:
        return False
    if acc_name in proxies:
        options.add_extension(f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_PATTERN}')
        print(f'[ INFO ] {acc_name}\'s proxy connected successfully\n')
    else:
        return False

    service = Service(config.CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options )
    driver.implicitly_wait(60)

    flag = proxy_checker(driver, acc_name)
    if not flag:
        driver.quit()
        return False


    login_url = 'https://getrich.tv/login'
    driver.get(login_url)

    a = input('Продолжить(Enter) >>')

    return True  



def main():
    # Create ness dirs 
    create_dirs()

    ref = proxies.db_init() 

    # Header 
    header_message = '___________GET_RICH___________\n'
    header_message += '| 1. Register a new account    |\n'
    header_message += '| 2. Add user data             |\n'
    header_message += '|                              |\n'
    header_message += '| 3. Start a farm              |\n'
    header_message += '|______________________________|'
    print(header_message)

    mode = input('\nEnter mode >> ')
    if not mode.isdigit():
        return False
    if 1 > int(mode) > 3:
        return False 
    
    acc_name = input('Acc name >> ')
    if int(mode) == 1:
        register_account(acc_name, ref)
    elif int(mode) == 2:
        add_user_data(acc_name)
    elif int(mode) == 3:
        pass
    

if __name__ == '__main__':
    main()