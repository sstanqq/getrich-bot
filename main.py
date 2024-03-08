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

import concurrent.futures

import config

from time import sleep

from utils import add_proxy, get_random_useragent, get_accs, load_user_data, \
                  proxy_validator, load_txt_data, email_validator, save_user_data, \
                  fake_user, move_to_dir, move_all

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
    for dir in [config.PROXIES_PATH, config.USERDATA_PATH, config.USERAGENTS_PATH, config.COMPLETED_PATH]:
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

    return email.strip(), password.strip()

def register_account(acc_name, ref):
    # Get New user-agent 
    get_random_useragent(acc_name)

    # Register new proxy
    flag = register_proxy(acc_name, ref)
    if not flag:
        print('[ERROR] Can\'t register a new proxy')
        return False 

    print('\nLocations:\n\
          \tNetherlands - nl_NL\n\
          \tGermany - de_DE\n\
          \tLatvia - lv_LV\n\
          \tSlovenia - sl_SI\n\
          \tDenmark - dk_DK\n\
          \tMoldova - mv_MV\n\
          \tUkraine - ua_UA')
    proxy_loc = input('Loc. >> ')

    user_email, user_password = add_user_data(acc_name)

    user_name, user_lastname = fake_user(proxy_loc)

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
    select_inputs = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'input-select__input')))

    name_input = text_inputs[0]
    lastname_input = text_inputs[1]
    nickname_input = text_inputs[2]
    email_input = text_inputs[3]
    pass_input = text_inputs[4]
    confirm_input = text_inputs[5]

    gender_input = select_inputs[0]
    city_input = select_inputs[1]

    # Enter text inputs 
    name_input.send_keys(user_name)
    lastname_input.send_keys(user_lastname)
    nickname_input.send_keys(acc_name)
    email_input.send_keys(user_email)
    pass_input.send_keys(user_password)
    confirm_input.send_keys(user_password)

    # Enter select inputs 
    gender_input.click()
    gender_dropdown_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='input-select__dropdown__item' and text()=' Male ']")))
    gender_dropdown_element.click()

    cities = {'nl_NL' : ' Netherlands ', 'de_DE' : ' Denmark ', 'lv_LV' : ' Latvia ', 'sl_SI' : ' Slovenia ', 'de_DE' : ' Denmark ', 'ua_UA' : ' Ukraine ', 'mv_MV' : ' Moldova '}
    city_input.click()
    filter_select = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'input-select__filter')))
    filter_select.send_keys(cities[proxy_loc].strip())
    city_dropdown_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@class='input-select__dropdown__item' and text()='{cities[proxy_loc]}']")))
    city_dropdown_element.click()

    try:
        agree_chb = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'pt-2')))
        driver.execute_script("arguments[0].click();", agree_chb)
    except:
        pass
    try:
        signup_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()=' Sign Up ']")))
        driver.execute_script("arguments[0].click();", signup_button)
    except:
        pass

    a = input('Продолжить(Enter) >>')

    driver.quit()


""" Automatization """
def authorization(driver, email, password):
    """ Login """
    wait = WebDriverWait(driver, 30)

    login_url = 'https://getrich.tv/login'
    driver.get(login_url)
    text_inputs = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'input-text__input')))

    email_input = text_inputs[0]
    email_input.send_keys(email)
    password_input = text_inputs[1]
    password_input.send_keys(password)

    sleep(5)

    try:
        signin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()=' Sign In ']")))
        driver.execute_script("arguments[0].click();", signin_btn)
    except Exception as e:
        print(e)

    sleep(5)

def set_quality(driver):
    wait = WebDriverWait(driver, 60)

    settings_btn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'player-controls__renditions-trigger')))
    settings_btn.click()

    quality_btns = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'player-controls__renditions-item')))
    quality_btns[1].click()

    sleep(60)

def get_balance(driver):
    wait = WebDriverWait(driver, 60)
    url = 'https://getrich.tv/my-dashboard'
    driver.get(url)
    withdraw_balance = 0 
    balance = 0

    try:
        balance_text = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'grid__text--70')))
        # print(balance_text.text.strip())
        withdraw_balance = float(balance_text.text.strip().split()[0])
    except Exception as e:
        print(e)
        print('[ERROR] Can\'t get balance')
    
    try:
        withdraw_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'grid__button')))
        withdraw_btn.click()
    except Exception as e:
        print(e)
        print('[ERROR] Can\'t withdraw money')

    try:
        cur_balance_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'account__balance-value')))
        cur_balance_spans = cur_balance_div.find_elements(By.TAG_NAME, 'span')
        balance = float(cur_balance_spans[1].text.strip())
    except Exception as e:
        print(e)
        print('[ERROR] Can\'t get balance')
    
    return withdraw_balance, balance

def get_progress(driver):
    wait = WebDriverWait(driver, 45)
    url = 'https://getrich.tv/my-dashboard'
    driver.get(url)

    progress_div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'grid__text--time')))
    progress_span = progress_div.find_element(By.TAG_NAME, 'span')
    progress = int(progress_span.text.replace('%', '').replace('✔', '').strip())

    url = 'https://getrich.tv'
    driver.get(url)

    return progress

def automatization_per_acc(acc_name, user_data, proxies, user_agents, buf_accs):

    if acc_name in user_data:
        user_email, user_password = load_user_data(acc_name)
        print(f'[INFO] {acc_name}\'s user data loaded successfully')
    else:
        return False

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
        buf_accs.remove(acc_name)
        return False
    if acc_name in proxies:
        options.add_extension(f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_PATTERN}')
        print(f'[ INFO ] {acc_name}\'s proxy connected successfully\n')
    else:
        buf_accs.remove(acc_name)
        return False

    service = Service(config.CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options )
    driver.implicitly_wait(60)

    flag = proxy_checker(driver, acc_name)
    if not flag:
        buf_accs.remove(acc_name)
        driver.quit()

    try:
        authorization(driver, user_email, user_password)

        set_quality(driver)

        cur_progress = 0
        while cur_progress < 100:
            cur_progress = get_progress(driver)
            print(f'\nAccount: {acc_name}')
            print(f'Progress: {cur_progress}\n')
            if cur_progress < 100:
                sleep(3*60)

        sleep(10)
        withdraw_balance, balance = get_balance(driver)
        print('\nReport:')
        print(f'\tAccount: {acc_name}')
        print(f'\t\tEarned today: {withdraw_balance}')
        print(f'\t\tTotal balance: {balance}\n')

        sleep(5)
        move_to_dir(acc_name, config.USERDATA_PATH, config.COMPLETED_PATH, config.USERDATA_PATTERN)
    except:
        buf_accs.remove(acc_name)

    driver.quit()

def automatization(threads_ammount):
    user_data = get_accs(config.USERDATA_PATTERN, config.USERDATA_PATH)
    proxies = get_accs(config.PROXIES_PATTERN, config.PROXIES_PATH)
    user_agents = get_accs(config.USERAGENT_PATTERN, config.USERAGENTS_PATH)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads_ammount) as executor:
        buf_accs = []
        try:
            while len(user_data) > 0:
                for acc_name in user_data:
                    if acc_name in buf_accs:
                        continue 

                    buf_accs.append(acc_name)
                    executor.submit(automatization_per_acc, acc_name, user_data, proxies, user_agents, buf_accs)

                    sleep(5)
            print('\n[INFO] Аккаунт отработаны')
        except:
            pass

    try:
        move_all(config.COMPLETED_PATH, config.USERDATA_PATH)
        print('[ INFO ] Аккаунты перемещены')
    except:
        print('[ ERROR ] Произошла ошибка перемещения')

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
    
    if int(mode) == 1:
        acc_name = input('Acc name >> ')
        register_account(acc_name, ref)
    elif int(mode) == 2:
        acc_name = input('Acc name >> ')
        add_user_data(acc_name)
    elif int(mode) == 3:
        threads_ammount = int(input('Threads >> '))
        automatization(threads_ammount)
    

if __name__ == '__main__':
    main()