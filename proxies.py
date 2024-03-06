import os
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Load values from .env
load_dotenv()
ADMIN_SDK = os.getenv('ADMIN_SDK')
DATABASE_URL = os.getenv('DATABASE_URL')

TABLE_NNAME = 'proxies'

# Connect to database 
def db_init():
    cred = credentials.Certificate(ADMIN_SDK)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    ref = db.reference(TABLE_NNAME)

    return ref

def get_proxies(ref):
    proxies = ref.get()

    return proxies

def add_proxy(ref, proxy_host, proxy_port):
    data = {'host' : proxy_host,
            'port' : proxy_port}
    try:
        ref.push(data)
    except Exception as e:
        print(f'[ERROR] {e}')
        return False 
    
    return True

def clear_db(ref):
    try:
        ref.delete()
    except:
        return False

    return True

def remove_proxy(ref, proxy_host):
    proxies_dict = get_proxies(ref)
    if proxies_dict is None:
        return True 
    
    for key, value in proxies_dict.items():
        if 'host' in value and value['host'] == proxy_host:
            ref.child(key).delete()

def check_proxy(ref, new_proxy_host):
    proxies_dict = get_proxies(ref)
    if proxies_dict is None:
        return True
    
    proxy_hosts = []
    for key, value in proxies_dict.items():
        if 'host' in value and value['host'] == new_proxy_host:
            return False
    
    return True