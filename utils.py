import config
import zipfile
import random 
import os

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

def load_user_agent(acc_name):
    with open(f'{config.USERAGENTS_PATH}/{acc_name}{config.USERAGENT_PATTERN}', 'r', encoding='utf-8') as file:
        content = file.read()
    
    return content.strip()

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

    print('[ INFO ] Proxy успешно добавлена\n')