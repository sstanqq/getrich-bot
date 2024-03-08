import config
import zipfile
import random 
import os
import re
import pickle
from faker import Faker
import shutil

def get_accs(pattern, dir):
    file_list = os.listdir(dir)

    for i in range(len(file_list)):
        file_list[i] = file_list[i].replace(pattern, '')

    return file_list

def get_random_useragent(acc_name):
    with open(config.USERAGENTS_FILE, 'r') as file:
        user_agents = file.readlines()

    random_user_agent = random.choice(user_agents)
    with open(f'{config.USERAGENTS_PATH}/{acc_name}{config.USERAGENT_PATTERN}', 'w') as file:
        file.write(random_user_agent.strip())

def load_txt_data(acc_name, path, pattern):
    with open(f'{path}/{acc_name}{pattern}', 'r', encoding='utf-8') as file:
        content = file.read()
    
    return content.strip()

def load_user_data(acc_name):
    with open(f'{config.USERDATA_PATH}/{acc_name}{config.USERDATA_PATTERN}', 'rb') as file:
        data = pickle.load(file)

    return data[0], data[1]

def save_user_data(acc_name, email, password):
    data = [email, password]
    with open(f'{config.USERDATA_PATH}/{acc_name}{config.USERDATA_PATTERN}', 'wb') as file:
        pickle.dump(data, file)
    return True 

def add_proxy(acc_name, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    let config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        }
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    )
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    plugin_file = f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_PATTERN}'

    with zipfile.ZipFile(plugin_file, 'w') as file:
        file.writestr('manifest.json', manifest_json)
        file.writestr('background.js', background_js)

    with open(f'{config.PROXIES_PATH}/{acc_name}{config.PROXIES_TXT_PATTERN}', 'w') as file:
        file.write(PROXY_HOST)

    print('[ INFO ] Proxy успешно добавлена\n')

def proxy_validator(proxy_host, proxy_port):
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if not re.match(ipv4_pattern, proxy_host):
        return False 
    if len(proxy_port) != 4:
        return False 
    
    return True

def email_validator(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True 
    return False

def fake_user(loc):
    if loc == 'mv_MV' or loc == 'ua_UA':
        loc = 'lv_LV'
    fake = Faker(loc)

    random_name = fake.first_name_male()
    random_lastname = fake.last_name_male()

    return random_name, random_lastname

def move_to_dir(acc_name, dir_src, dir_dist, pattern):
    shutil.move(dir_src+'/'+acc_name+pattern, dir_dist+'/'+acc_name+pattern)

# Перемещение всех файлов
def move_all(dir_src, dir_dist):
    file_list = os.listdir(dir_src)

    for file in file_list:
        shutil.move(dir_src+'/'+file, dir_dist+'/'+file)