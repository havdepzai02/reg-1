#!/usr/bin/env python3
import hmac
import hashlib
import requests
import string
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import codecs
import time
from datetime import datetime
from colorama import Fore, Style, init
import urllib3
import os
import sys
import base64
import signal
import threading
import psutil
import re
import subprocess
import importlib
import socks
import socket

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ====================== TOR INTEGRATION ======================
def start_tor():
    """Khởi động Tor service"""
    try:
        # Kiểm tra xem Tor đã chạy chưa
        tor_process = subprocess.Popen(['tor'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
        print(f"{Fore.GREEN}[+] Tor started successfully!{Style.RESET_ALL}")
        return tor_process
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Tor not installed. Please install tor first.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Could not start Tor: {e}{Style.RESET_ALL}")
        return None

def stop_tor(tor_process):
    """Dừng Tor service"""
    if tor_process:
        tor_process.terminate()
        tor_process.wait()

def change_tor_ip():
    """Thay đổi IP của Tor bằng cách gửi tín hiệu HUP"""
    try:
        # Gửi tín hiệu HUP đến Tor để thay đổi circuit
        subprocess.run(['pkill', '-HUP', 'tor'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(3)  # Chờ Tor thiết lập circuit mới
        return True
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Failed to change Tor IP: {e}{Style.RESET_ALL}")
        return False

def get_current_ip():
    """Lấy IP hiện tại thông qua Tor"""
    try:
        # Thiết lập socket để sử dụng SOCKS proxy của Tor
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        
        response = requests.get("https://checkip.amazonaws.com", timeout=10)
        return response.text.strip()
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Failed to get IP: {e}{Style.RESET_ALL}")
        return "Unknown"

def rotate_ip_if_needed():
    """Quản lý việc thay đổi IP sau mỗi 100 tài khoản"""
    global ACCOUNTS_PER_IP
    
    with ACCOUNTS_PER_IP['lock']:
        ACCOUNTS_PER_IP['count'] += 1
        
        if ACCOUNTS_PER_IP['count'] >= 100:
            print(f"{Fore.CYAN}[+] Reached {ACCOUNTS_PER_IP['count']} accounts, rotating IP...{Style.RESET_ALL}")
            
            if change_tor_ip():
                new_ip = get_current_ip()
                ACCOUNTS_PER_IP['count'] = 0
                ACCOUNTS_PER_IP['ip'] = new_ip
                print(f"{Fore.GREEN}[✓] IP changed successfully! New IP: {new_ip}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}[!] Failed to rotate IP{Style.RESET_ALL}")
                return False
    return True

# ====================== GLOBAL VARIABLES ======================
ACCOUNTS_PER_IP = {
    'count': 0,
    'ip': 'Unknown',
    'lock': threading.Lock()
}

def get_random_color():
    colors = [Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTBLUE_EX]
    return random.choice(colors)

class Colors:
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL

EXIT_FLAG = False
SUCCESS_COUNTER = 0
TARGET_ACCOUNTS = 0
RARE_COUNTER = 0
COUPLES_COUNTER = 0
RARITY_SCORE_THRESHOLD = 3
LOCK = threading.Lock()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.join(CURRENT_DIR, "SPIDEERIO-ERA")
TOKENS_FOLDER = os.path.join(BASE_FOLDER, "TOKENS-JWT")
ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "ACCOUNTS")
RARE_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "RARE ACCOUNTS")
COUPLES_ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "COUPLES ACCOUNTS")
GHOST_FOLDER = os.path.join(BASE_FOLDER, "GHOST")
GHOST_ACCOUNTS_FOLDER = os.path.join(GHOST_FOLDER, "ACCOUNTS")
GHOST_RARE_FOLDER = os.path.join(GHOST_FOLDER, "RAREACCOUNT")
GHOST_COUPLES_FOLDER = os.path.join(GHOST_FOLDER, "COUPLESACCOUNT")

for folder in [BASE_FOLDER, TOKENS_FOLDER, ACCOUNTS_FOLDER, RARE_ACCOUNTS_FOLDER, 
               COUPLES_ACCOUNTS_FOLDER, GHOST_FOLDER, GHOST_ACCOUNTS_FOLDER, 
               GHOST_RARE_FOLDER, GHOST_COUPLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th", 
    "BD": "bn", "PK": "ur", "TW": "zh", "CIS": "ru", "SAC": "es", "BR": "pt"
}

REGION_URLS = {
    "IND": "https://client.ind.freefiremobile.com/",
    "ID": "https://clientbp.ggblueshark.com/",
    "BR": "https://client.us.freefiremobile.com/",
    "ME": "https://clientbp.common.ggbluefox.com/",
    "VN": "https://clientbp.ggblueshark.com/",
    "TH": "https://clientbp.common.ggbluefox.com/",
    "CIS": "https://clientbp.ggblueshark.com/",
    "BD": "https://clientbp.ggblueshark.com/",
    "PK": "https://clientbp.ggblueshark.com/",
    "SG": "https://clientbp.ggblueshark.com/",
    "SAC": "https://client.us.freefiremobile.com/",
    "TW": "https://clientbp.ggblueshark.com/"
}

hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)
hex_data = "8J+agCBQUkVNSVVNIEFDQ09VTlQgR0VORVJBVE9SIPCfkqsgQnkgU1BJREVFUklPIHwgTm90IEZvciBTYWxlIPCfkas="
client_data = base64.b64decode(hex_data).decode('utf-8')
GARENA = "QllfU1BJREVFUklPX0dBTUlORw=="

FILE_LOCKS = {}

def get_file_lock(filename):
    if filename not in FILE_LOCKS:
        FILE_LOCKS[filename] = threading.Lock()
    return FILE_LOCKS[filename]

ACCOUNT_RARITY_PATTERNS = {
    "REPEATED_DIGITS_4": [r"(\d)\1{3,}", 3],
    "REPEATED_DIGITS_3": [r"(\d)\1\1(\d)\2\2", 2],
    "SEQUENTIAL_5": [r"(12345|23456|34567|45678|56789)", 4],
    "SEQUENTIAL_4": [r"(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)", 3],
    "PALINDROME_6": [r"^(\d)(\d)(\d)\3\2\1$", 5],
    "PALINDROME_4": [r"^(\d)(\d)\2\1$", 3],
    "SPECIAL_COMBINATIONS_HIGH": [r"(69|420|1337|007)", 4],
    "SPECIAL_COMBINATIONS_MED": [r"(100|200|300|400|500|666|777|888|999)", 2],
    "QUADRUPLE_DIGITS": [r"(1111|2222|3333|4444|5555|6666|7777|8888|9999|0000)", 4],
    "MIRROR_PATTERN_HIGH": [r"^(\d{2,3})\1$", 3],
    "MIRROR_PATTERN_MED": [r"(\d{2})0\1", 2],
    "GOLDEN_RATIO": [r"1618|0618", 3]
}

ACCOUNT_COUPLES_PATTERNS = {
    "MATCHING_PAIRS": [
        r"(\d{2})01.*\d{2}02",
        r"(\d{2})11.*\d{2}12",
        r"(\d{2})21.*\d{2}22",
    ],
    "COMPLEMENTARY_DIGITS": [
        r".*13.*14$",
        r".*07.*08$",
        r".*51.*52$",
    ],
    "LOVE_NUMBERS": [
        r".*520.*521$",
        r".*1314$",
    ]
}

POTENTIAL_COUPLES = {}
COUPLES_LOCK = threading.Lock()

# ====================== TOR-AWARE REQUESTS ======================
def tor_request(method, url, **kwargs):
    """Thực hiện request thông qua Tor"""
    try:
        # Thiết lập proxy Tor cho requests
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        response = requests.request(method, url, proxies=proxies, 
                                   timeout=30, verify=False, **kwargs)
        return response
    except Exception as e:
        print(f"{Fore.YELLOW}[!] Tor request failed: {e}{Style.RESET_ALL}")
        # Fallback to normal request
        return requests.request(method, url, timeout=30, verify=False, **kwargs)

# ====================== MODIFIED FUNCTIONS ======================
def create_acc(region, account_name, password_prefix, is_ghost=False):
    """Tạo tài khoản với Tor"""
    if EXIT_FLAG:
        return None
    try:
        password = generate_custom_password(password_prefix)
        data = f"password={password}&client_type=2&source=2&app_id=100067"
        message = data.encode('utf-8')
        signature = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        url = "https://100067.connect.garena.com/oauth/guest/register"
        headers = {
            "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
            "Authorization": "Signature " + signature,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        
        # Sử dụng tor_request thay vì requests trực tiếp
        response = tor_request('POST', url, headers=headers, data=data)
        response.raise_for_status()
        
        if 'uid' in response.json():
            uid = response.json()['uid']
            print_success(f"Guest account created: {uid}")
            smart_delay()
            return token(uid, password, region, account_name, password_prefix, is_ghost)
        return None
    except Exception as e:
        print_warning(f"Create account failed: {e}")
        smart_delay()
        return None

def token(uid, password, region, account_name, password_prefix, is_ghost=False):
    """Lấy token với Tor"""
    if EXIT_FLAG:
        return None
    try:
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P8(ASUS_Z01QD ;Android 12;en;US;)",
        }
        body = {
            "uid": uid,
            "password": password,
            "response_type": "token",
            "client_type": "2",
            "client_secret": key,
            "client_id": "100067"
        }
        
        # Sử dụng tor_request
        response = tor_request('POST', url, headers=headers, data=body)
        response.raise_for_status()
        
        if 'open_id' in response.json():
            open_id = response.json()['open_id']
            access_token = response.json()["access_token"]
            refresh_token = response.json()['refresh_token']
            
            result = encode_string(open_id)
            field = to_unicode_escaped(result['field_14'])
            field = codecs.decode(field, 'unicode_escape').encode('latin1')
            print_success(f"Token granted for: {uid}")
            smart_delay()
            return Major_Regsiter(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost)
        return None
    except Exception as e:
        print_warning(f"Token grant failed: {e}")
        smart_delay()
        return None

def Major_Regsiter(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost=False):
    """Đăng ký tài khoản chính với Tor"""
    if EXIT_FLAG:
        return None
    try:
        if is_ghost:
            url = "https://loginbp.ggblueshark.com/MajorRegister"
        else:
            if region.upper() in ["ME", "TH"]:
                url = "https://loginbp.common.ggbluefox.com/MajorRegister"
            else:
                url = "https://loginbp.ggblueshark.com/MajorRegister"
            
        name = generate_random_name(account_name)
        
        headers = {
            "Accept-Encoding": "gzip",
            "Authorization": "Bearer",   
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue",
            "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME", "TH"] else "loginbp.common.ggbluefox.com",
            "ReleaseVersion": "OB52",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4."
        }

        lang_code = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        payload = {
            1: name,
            2: access_token,
            3: open_id,
            5: 102000007,
            6: 4,
            7: 1,
            13: 1,
            14: field,
            15: lang_code,
            16: 1,
            17: 1
        }

        payload_bytes = CrEaTe_ProTo(payload)
        encrypted_payload = E_AEs(payload_bytes.hex())
        
        # Sử dụng tor_request
        response = tor_request('POST', url, headers=headers, data=encrypted_payload)
        
        if response.status_code == 200:
            print_success(f"MajorRegister successful: {name}")
            
            login_result = perform_major_login(uid, password, access_token, open_id, region, is_ghost)
            account_id = login_result.get("account_id", "N/A")
            jwt_token = login_result.get("jwt_token", "")
            
            if not is_ghost and jwt_token and account_id != "N/A" and region.upper() != "BR":
                region_bound = force_region_binding(region, jwt_token)
                if region_bound:
                    print_success(f"Region {region} bound successfully!")
                else:
                    print_warning(f"Region binding failed for {region}")
            
            account_data = {
                "uid": uid, 
                "password": password, 
                "name": name, 
                "region": "GHOST" if is_ghost else region, 
                "status": "success",
                "account_id": account_id,
                "jwt_token": jwt_token
            }
            
            return account_data
        else:
            print_warning(f"MajorRegister returned status: {response.status_code}")
            return None
    except Exception as e:
        print_warning(f"Major_Regsiter error: {str(e)}")
        smart_delay()
        return None

def perform_major_login(uid, password, access_token, open_id, region, is_ghost=False):
    """Đăng nhập tài khoản chính với Tor"""
    try:
        lang = "pt" if is_ghost else REGION_LANG.get(region.upper(), "en")
        
        payload_parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        
        payload = b''.join(payload_parts)
        
        if is_ghost:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        elif region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/MajorLogin"
        else:
            url = "https://loginbp.ggblueshark.com/MajorLogin"
        
        headers = {
            "Accept-Encoding": "gzip",
            "Authorization": "Bearer",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue",
            "Host": "loginbp.ggblueshark.com" if is_ghost or region.upper() not in ["ME", "TH"] else "loginbp.common.ggbluefox.com",
            "ReleaseVersion": "OB52",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1"
        }

        data = payload
        data = data.replace(b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390', access_token.encode())
        data = data.replace(b'1d8ec0240ede109973f3321b9354b44d', open_id.encode())
        
        d = encrypt_api(data.hex())
        final_payload = bytes.fromhex(d)

        # Sử dụng tor_request
        response = tor_request('POST', url, headers=headers, data=final_payload)
        
        if response.status_code == 200 and len(response.text) > 10:
            jwt_start = response.text.find("eyJ")
            if jwt_start != -1:
                jwt_token = response.text[jwt_start:]
                second_dot = jwt_token.find(".", jwt_token.find(".") + 1)
                if second_dot != -1:
                    jwt_token = jwt_token[:second_dot + 44]
                    
                    account_id = decode_jwt_token(jwt_token)
                    return {"account_id": account_id, "jwt_token": jwt_token}
        
        return {"account_id": "N/A", "jwt_token": ""}
    except Exception as e:
        print_warning(f"MajorLogin failed: {e}")
        return {"account_id": "N/A", "jwt_token": ""}

def force_region_binding(region, jwt_token):
    """Binding region với Tor"""
    try:
        if region.upper() in ["ME", "TH"]:
            url = "https://loginbp.common.ggbluefox.com/ChooseRegion"
        else:
            url = "https://loginbp.ggblueshark.com/ChooseRegion"
        
        if region.upper() == "CIS":
            region_code = "RU"
        else:
            region_code = region.upper()
            
        fields = {1: region_code}
        proto_data = CrEaTe_ProTo(fields)
        encrypted_data = encrypt_api(proto_data.hex())
        payload = bytes.fromhex(encrypted_data)
        
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'Expect': "100-continue",
            'Authorization': f"Bearer {jwt_token}",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB52"
        }
        
        # Sử dụng tor_request
        response = tor_request('POST', url, data=payload, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print_warning(f"Region binding failed: {e}")
        return False

# ====================== MODIFIED WORKER FUNCTION ======================
def worker(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    """Worker thread với IP rotation"""
    thread_color = get_random_color()
    print(f"{thread_color}{Colors.BRIGHT}🧵 Thread {thread_id} started{Colors.RESET}")
    
    accounts_generated = 0
    while not EXIT_FLAG:
        with LOCK:
            if SUCCESS_COUNTER >= total_accounts:
                break
        
        # Kiểm tra và thay đổi IP nếu cần
        rotate_ip_if_needed()
        
        result = generate_single_account(region, account_name, password_prefix, 
                                        total_accounts, thread_id, is_ghost)
        if result:
            accounts_generated += 1
        
        # Delay ngẫu nhiên để tránh detection
        time.sleep(random.uniform(1, 3))
    
    print(f"{thread_color}{Colors.BRIGHT}🧵 Thread {thread_id} finished: {accounts_generated} accounts generated{Colors.RESET}")

# ====================== MODIFIED MAIN FLOW ======================
def generate_accounts_flow():
    """Luồng chính với Tor integration"""
    global SUCCESS_COUNTER, TARGET_ACCOUNTS, RARE_COUNTER, COUPLES_COUNTER, RARITY_SCORE_THRESHOLD
    
    # Khởi động Tor
    print(f"{Fore.CYAN}[+] Starting Tor service...{Style.RESET_ALL}")
    tor_process = start_tor()
    if not tor_process:
        print(f"{Fore.RED}[!] Cannot continue without Tor{Style.RESET_ALL}")
        wait_for_enter()
        return
    
    try:
        clear_screen()
        display_banner()
        
        cpu_count = psutil.cpu_count()
        recommended_threads = min(cpu_count, 3)
        
        print(f"{get_random_color()}{Colors.BRIGHT}🌍 Available Regions:{Colors.RESET}")
        
        regions_to_show = [region for region in REGION_LANG.keys() if region != "BR"]
        
        for i, region in enumerate(regions_to_show, 1):
            print(f"{get_random_color()}{i}) {get_random_color()}{region} ({REGION_LANG[region]}){Colors.RESET}")
        
        print(f"{get_random_color()}{len(regions_to_show)+1}) {Fore.LIGHTMAGENTA_EX}GHOST Mode{Colors.RESET}")
        print(f"{get_random_color()}00) {Fore.YELLOW}Back to Main Menu{Colors.RESET}")
        print(f"{get_random_color()}000) {Fore.RED}Exit{Colors.RESET}")

        while True:
            try:
                choice = input(f"\n{get_random_color()}{Colors.BRIGHT}🎯 Choose option: {Colors.RESET}").strip().upper()
                
                if choice == "00":
                    stop_tor(tor_process)
                    return
                elif choice == "000":
                    print(f"\n{get_random_color()}{Colors.BRIGHT}👋 Thank you for using SPIDEERIO Generator!{Colors.RESET}")
                    stop_tor(tor_process)
                    sys.exit(0)
                elif choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(regions_to_show):
                        selected_region = regions_to_show[choice_num - 1]
                        is_ghost = False
                        break
                    elif choice_num == len(regions_to_show) + 1:
                        selected_region = "BR"
                        is_ghost = True
                        break
                    else:
                        print_error("Invalid option. Please choose a valid number.")
                elif choice in regions_to_show:
                    selected_region = choice
                    is_ghost = False
                    break
                elif choice == "GHOST":
                    selected_region = "BR"
                    is_ghost = True
                    break
                else:
                    print_error("Invalid option. Please choose a valid region.")
            except ValueError:
                print_error("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                stop_tor(tor_process)
                safe_exit()

        clear_screen()
        display_banner()
        
        # Hiển thị IP hiện tại
        current_ip = get_current_ip()
        print(f"{Fore.CYAN}[+] Current Tor IP: {current_ip}{Style.RESET_ALL}")
        ACCOUNTS_PER_IP['ip'] = current_ip
        
        if is_ghost:
            print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}🌍 Selected Mode: GHOST MODE{Colors.RESET}")
        else:
            print(f"{get_random_color()}{Colors.BRIGHT}🌍 Selected Region: {selected_region} ({REGION_LANG[selected_region]}){Colors.RESET}")

        while True:
            try:
                account_count = int(input(f"\n{get_random_color()}{Colors.BRIGHT}🎯 Total Accounts to Generate: {Colors.RESET}"))
                if account_count > 0:
                    break
                else:
                    print_error("Please enter a positive number.")
            except ValueError:
                print_error("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                stop_tor(tor_process)
                safe_exit()

        while True:
            account_name = input(f"\n{get_random_color()}{Colors.BRIGHT}👤 Enter account name prefix: {Colors.RESET}").strip()
            if account_name:
                break
            else:
                print_error("Account name cannot be empty.")

        while True:
            password_prefix = input(f"\n{get_random_color()}{Colors.BRIGHT}🔑 Enter password prefix: {Colors.RESET}").strip()
            if password_prefix:
                break
            else:
                print_error("Password prefix cannot be empty.")

        while True:
            try:
                rarity_threshold = int(input(f"\n{get_random_color()}{Colors.BRIGHT}⭐ Rarity Threshold (2-10): {Colors.RESET}"))
                if 1 <= rarity_threshold <= 10:
                    RARITY_SCORE_THRESHOLD = rarity_threshold
                    break
                else:
                    print_error("Please enter a number between 1 and 10.")
            except ValueError:
                print_error("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                stop_tor(tor_process)
                safe_exit()

        while True:
            try:
                thread_count = int(input(f"\n{get_random_color()}{Colors.BRIGHT}🧵 Thread Count (Recommended: {recommended_threads}): {Colors.RESET}"))
                if thread_count > 0:
                    break
                else:
                    print_error("Thread count must be positive.")
            except ValueError:
                print_error("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                stop_tor(tor_process)
                safe_exit()

        clear_screen()
        display_banner()
        
        # Hiển thị thông tin Tor
        print(f"{Fore.CYAN}[+] Tor Status: ACTIVE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] Current IP: {ACCOUNTS_PER_IP['ip']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[+] IP will rotate every 100 accounts{Style.RESET_ALL}")
        
        if is_ghost:
            print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}🚀 Starting GHOST MODE Account Generation{Colors.RESET}")
        else:
            print(f"{get_random_color()}{Colors.BRIGHT}🚀 Starting Account Generation for {selected_region}{Colors.RESET}")
        
        print(f"{get_random_color()}{Colors.BRIGHT}🎯 Target Accounts: {account_count}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}👤 Name Prefix: {account_name}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}🔑 Password Prefix: {password_prefix}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}⭐ Rarity Threshold: {RARITY_SCORE_THRESHOLD}+{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}🧵 Threads: {thread_count}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}📁 Saving to: {ACCOUNTS_FOLDER}{Colors.RESET}")
        print(f"\n{get_random_color()}{Colors.BRIGHT}⏳ Starting in 3 seconds...{Colors.RESET}")
        time.sleep(3)

        # Reset counters
        SUCCESS_COUNTER = 0
        TARGET_ACCOUNTS = account_count
        RARE_COUNTER = 0
        COUPLES_COUNTER = 0
        ACCOUNTS_PER_IP['count'] = 0
        
        start_time = time.time()
        threads = []

        print(f"\n{get_random_color()}{Colors.BRIGHT}🚀 Starting generation with {thread_count} threads...{Colors.RESET}\n")

        # Khởi động các thread
        for i in range(thread_count):
            t = threading.Thread(target=worker, args=(selected_region, account_name, 
                                                     password_prefix, account_count, 
                                                     i+1, is_ghost))
            t.daemon = True
            t.start()
            threads.append(t)

        try:
            # Theo dõi tiến trình
            while any(t.is_alive() for t in threads):
                time.sleep(2)
                with LOCK:
                    current_count = SUCCESS_COUNTER
                
                progress = (current_count / account_count) * 100
                print(f"{get_random_color()}{Colors.BRIGHT}📊 Progress: {current_count}/{account_count} ({progress:.1f}%) | "
                      f"💎 Rare: {RARE_COUNTER} | 💑 Couples: {COUPLES_COUNTER} | "
                      f"🌐 IP: {ACCOUNTS_PER_IP['ip']}{Colors.RESET}")
                
                if current_count >= account_count:
                    break
                    
        except KeyboardInterrupt:
            print_warning("Generation interrupted by user!")
            EXIT_FLAG = True
            for t in threads:
                t.join(timeout=1)

        # Chờ các thread hoàn thành
        for t in threads:
            t.join(timeout=5)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Hiển thị kết quả
        print(f"\n{get_random_color()}{Colors.BRIGHT}🎉 Generation completed!{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}📊 Accounts generated: {SUCCESS_COUNTER}/{account_count}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}💎 Rare accounts found: {RARE_COUNTER}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}💑 Couples pairs found: {COUPLES_COUNTER}{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}🌐 IP rotations: {ACCOUNTS_PER_IP['count']} times{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}⭐ Rarity threshold used: {RARITY_SCORE_THRESHOLD}+{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}⏱️ Time taken: {elapsed_time:.2f} seconds{Colors.RESET}")
        print(f"{get_random_color()}{Colors.BRIGHT}⚡ Speed: {SUCCESS_COUNTER/elapsed_time:.2f} accounts/second{Colors.RESET}")
        
        if is_ghost:
            print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}📁 GHOST accounts saved in: {GHOST_ACCOUNTS_FOLDER}{Colors.RESET}")
            print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}💎 Rare GHOST accounts saved in: {GHOST_RARE_FOLDER}{Colors.RESET}")
            print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}💑 Couples GHOST accounts saved in: {GHOST_COUPLES_FOLDER}{Colors.RESET}")
        else:
            print(f"{get_random_color()}{Colors.BRIGHT}📁 Accounts saved in: {ACCOUNTS_FOLDER}{Colors.RESET}")
            print(f"{get_random_color()}{Colors.BRIGHT}💎 Rare accounts saved in: {RARE_ACCOUNTS_FOLDER}{Colors.RESET}")
            print(f"{get_random_color()}{Colors.BRIGHT}💑 Couples accounts saved in: {COUPLES_ACCOUNTS_FOLDER}{Colors.RESET}")
            print(f"{get_random_color()}{Colors.BRIGHT}🔐 JWT tokens saved in: {TOKENS_FOLDER}{Colors.RESET}")
        
    finally:
        # Luôn dừng Tor khi hoàn thành
        print(f"\n{Fore.CYAN}[+] Stopping Tor service...{Style.RESET_ALL}")
        stop_tor(tor_process)
    
    wait_for_enter()

# ====================== CÁC HÀM KHÁC GIỮ NGUYÊN ======================
# (Giữ nguyên tất cả các hàm khác từ code gốc)
# [Tất cả các hàm còn lại giữ nguyên]

# Chỉ cần thêm import socks ở đầu file
# pip install PySocks

if __name__ == "__main__":
    try:
        if install_requirements():
            main_menu()
    except KeyboardInterrupt:
        safe_exit()
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        print(f"\n{Fore.YELLOW}{Colors.BRIGHT}🔄 Restarting script...{Colors.RESET}")
        time.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
