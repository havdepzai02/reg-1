# 1.py - Generator gửi accounts lên server sg-sgp05.altr.cc:25403
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
import traceback

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== PHẦN WEB SAVER TÍCH HỢP ==========

class WebSaver:
    """Class để gửi data lên web server"""
    
    def __init__(self, server_url="http://sg-sgp05.altr.cc:25403"):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.max_retries = 3
        self.retry_delay = 2
        
        # Disable SSL warnings
        import warnings
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        print(f"{Fore.CYAN}🔗 WebSaver initialized: {server_url}{Style.RESET_ALL}")
    
    def check_connection(self):
        """Kiểm tra kết nối đến server"""
        try:
            response = self.session.get(
                f"{self.server_url}/api/health", 
                timeout=10,
                verify=False
            )
            if response.status_code == 200:
                data = response.json()
                print(f"{Fore.GREEN}✅ Connected to server: {self.server_url}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📊 Server stats: {data.get('total_accounts', 0)} accounts{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}⚠️ Server returned status: {response.status_code}{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Cannot connect to server: {str(e)[:100]}{Style.RESET_ALL}")
            return False
    
    def _send_with_retry(self, endpoint, data):
        """Gửi request với retry"""
        for attempt in range(self.max_retries):
            try:
                url = f"{self.server_url}{endpoint}"
                response = self.session.post(
                    url,
                    json=data,
                    timeout=30,
                    verify=False,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except:
                        return {"status": "success"}
                elif response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                
                return {"status": "error", "code": response.status_code}
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {"status": "timeout"}
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {"status": "error", "message": str(e)}
        
        return {"status": "max_retries_exceeded"}
    
    def save_account(self, account_data):
        """Gửi account lên server"""
        result = self._send_with_retry("/api/save_account", account_data)
        
        if result.get("status") == "success":
            print(f"{Fore.GREEN}✅ Account saved to server{Style.RESET_ALL}")
            return True
        elif result.get("status") == "duplicate":
            print(f"{Fore.YELLOW}⚠️ Account already exists on server{Style.RESET_ALL}")
            return True
        else:
            error_msg = result.get('message', f"Code: {result.get('code', 'Unknown')}")
            print(f"{Fore.RED}❌ Failed to save account: {error_msg}{Style.RESET_ALL}")
            return False
    
    def save_rare_account(self, rare_data):
        """Gửi rare account lên server"""
        result = self._send_with_retry("/api/save_rare_account", rare_data)
        
        if result.get("status") == "success":
            print(f"{Fore.MAGENTA}💎 Rare account saved to server{Style.RESET_ALL}")
            return True
        else:
            error_msg = result.get('message', f"Code: {result.get('code', 'Unknown')}")
            print(f"{Fore.RED}❌ Failed to save rare account: {error_msg}{Style.RESET_ALL}")
            return False
    
    def save_couples_account(self, couples_data):
        """Gửi couples account lên server"""
        result = self._send_with_retry("/api/save_couples_account", couples_data)
        
        if result.get("status") == "success":
            print(f"{Fore.CYAN}💑 Couples account saved to server{Style.RESET_ALL}")
            return True
        else:
            error_msg = result.get('message', f"Code: {result.get('code', 'Unknown')}")
            print(f"{Fore.RED}❌ Failed to save couples account: {error_msg}{Style.RESET_ALL}")
            return False
    
    def save_token(self, token_data):
        """Gửi token lên server"""
        result = self._send_with_retry("/api/save_token", token_data)
        
        if result.get("status") == "success":
            print(f"{Fore.BLUE}🔐 Token saved to server{Style.RESET_ALL}")
            return True
        else:
            error_msg = result.get('message', f"Code: {result.get('code', 'Unknown')}")
            print(f"{Fore.RED}❌ Failed to save token: {error_msg}{Style.RESET_ALL}")
            return False
    
    def get_stats(self):
        """Lấy thống kê từ server"""
        try:
            response = self.session.get(
                f"{self.server_url}/api/get_stats",
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Get stats error: {e}{Style.RESET_ALL}")
            return None

# Khởi tạo WebSaver
WEB_SAVER = WebSaver(server_url="http://sg-sgp05.altr.cc:25403")
USE_WEB_SAVER = True  # Luôn bật web saver

def send_account_async(account_data):
    """Gửi account bất đồng bộ"""
    def send():
        WEB_SAVER.save_account(account_data)
    
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()

def send_rare_account_async(rare_data):
    """Gửi rare account bất đồng bộ"""
    def send():
        WEB_SAVER.save_rare_account(rare_data)
    
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()

def send_couples_account_async(couples_data):
    """Gửi couples account bất đồng bộ"""
    def send():
        WEB_SAVER.save_couples_account(couples_data)
    
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()

def send_token_async(token_data):
    """Gửi token bất đồng bộ"""
    def send():
        WEB_SAVER.save_token(token_data)
    
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()

# ========== PHẦN GỐC CỦA 1.py ==========

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

# Không cần tạo thư mục local nữa
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

REGION_LANG = {"ME": "ar","IND": "hi","ID": "id","VN": "vi","TH": "th","BD": "bn","PK": "ur","TW": "zh","CIS": "ru","SAC": "es","BR": "pt"}
REGION_URLS = {"IND": "https://client.ind.freefiremobile.com/","ID": "https://clientbp.ggblueshark.com/","BR": "https://client.us.freefiremobile.com/","ME": "https://clientbp.common.ggbluefox.com/","VN": "https://clientbp.ggblueshark.com/","TH": "https://clientbp.common.ggbluefox.com/","CIS": "https://clientbp.ggblueshark.com/","BD": "https://clientbp.ggblueshark.com/","PK": "https://clientbp.ggblueshark.com/","SG": "https://clientbp.ggblueshark.com/","SAC": "https://client.us.freefiremobile.com/","TW": "https://clientbp.ggblueshark.com/"}
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)
hex_data = "U2FqZWViIEFoYW1lZCBQcmVtaXVtIEFjY291bnQgR2VuZXJhdG9y8J+OoA=="
client_data = base64.b64decode(hex_data).decode('utf-8')
GARENA = "QllfU0FKRUViX0FIQU1FRA=="

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

def check_account_rarity(account_data):
    account_id = account_data.get("account_id", "")
    
    if account_id == "N/A" or not account_id:
        return False, None, None, 0
    
    rarity_score = 0
    detected_patterns = []
    
    for rarity_type, pattern_data in ACCOUNT_RARITY_PATTERNS.items():
        pattern = pattern_data[0]
        score = pattern_data[1]
        if re.search(pattern, account_id):
            rarity_score += score
            detected_patterns.append(rarity_type)
    
    account_id_digits = [int(d) for d in account_id if d.isdigit()]
    
    if len(set(account_id_digits)) == 1 and len(account_id_digits) >= 4:
        rarity_score += 5
        detected_patterns.append("UNIFORM_DIGITS")
    
    if len(account_id_digits) >= 4:
        differences = [account_id_digits[i+1] - account_id_digits[i] for i in range(len(account_id_digits)-1)]
        if len(set(differences)) == 1:
            rarity_score += 4
            detected_patterns.append("ARITHMETIC_SEQUENCE")
    
    if len(account_id) <= 8 and account_id.isdigit() and int(account_id) < 1000000:
        rarity_score += 3
        detected_patterns.append("LOW_ACCOUNT_ID")
    
    if rarity_score >= RARITY_SCORE_THRESHOLD:
        reason = f"Account ID {account_id} - Score: {rarity_score} - Patterns: {', '.join(detected_patterns)}"
        return True, "RARE_ACCOUNT", reason, rarity_score
    
    return False, None, None, rarity_score

def check_account_couples(account_data, thread_id):
    account_id = account_data.get("account_id", "")
    
    if account_id == "N/A" or not account_id:
        return False, None, None
    
    with COUPLES_LOCK:
        for stored_id, stored_data in POTENTIAL_COUPLES.items():
            stored_account_id = stored_data.get('account_id', '')
            
            couple_found, reason = check_account_couple_patterns(account_id, stored_account_id)
            if couple_found:
                partner_data = stored_data
                del POTENTIAL_COUPLES[stored_id]
                return True, reason, partner_data
        
        POTENTIAL_COUPLES[account_id] = {
            'uid': account_data.get('uid', ''),
            'account_id': account_id,
            'name': account_data.get('name', ''),
            'password': account_data.get('password', ''),
            'region': account_data.get('region', ''),
            'thread_id': thread_id,
            'timestamp': datetime.now().isoformat()
        }
    
    return False, None, None

def check_account_couple_patterns(account_id1, account_id2):
    if account_id1 and account_id2 and abs(int(account_id1) - int(account_id2)) == 1:
        return True, f"Sequential Account IDs: {account_id1} & {account_id2}"
    
    if account_id1 == account_id2[::-1]:
        return True, f"Mirror Account IDs: {account_id1} & {account_id2}"
    
    if account_id1 and account_id2:
        sum_acc = int(account_id1) + int(account_id2)
        if sum_acc % 1000 == 0 or sum_acc % 10000 == 0:
            return True, f"Complementary sum: {account_id1} + {account_id2} = {sum_acc}"
    
    love_numbers = ['520', '521', '1314', '3344']
    for love_num in love_numbers:
        if love_num in account_id1 and love_num in account_id2:
            return True, f"Both contain love number: {love_num}"
    
    return False, None

def save_rare_account(account_data, rarity_type, reason, rarity_score, is_ghost=False):
    """Lưu rare account (gửi lên server)"""
    try:
        # Chuẩn bị rare data cho web
        rare_data = {
            'uid': account_data["uid"],
            'password': account_data["password"],
            'account_id': account_data.get("account_id", "N/A"),
            'name': account_data["name"],
            'region': "SAJEEB" if is_ghost else account_data.get('region', 'UNKNOWN'),
            'rarity_type': rarity_type,
            'rarity_score': rarity_score,
            'reason': reason,
            'thread_id': account_data.get('thread_id', 'N/A'),
            'is_ghost': is_ghost,
            'jwt_token': account_data.get('jwt_token', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Gửi bất đồng bộ lên server
        send_rare_account_async(rare_data)
        return True
        
    except Exception as e:
        print_error(f"Error saving rare account: {e}")
        return False

def save_couples_account(account1, account2, reason, is_ghost=False):
    """Lưu couples account (gửi lên server)"""
    try:
        couples_data = {
            'couple_id': f"{account1.get('account_id', 'N/A')}_{account2.get('account_id', 'N/A')}",
            'account1': {
                'uid': account1["uid"],
                'password': account1["password"],
                'account_id': account1.get("account_id", "N/A"),
                'name': account1["name"],
                'thread_id': account1.get('thread_id', 'N/A')
            },
            'account2': {
                'uid': account2["uid"],
                'password': account2["password"],
                'account_id': account2.get("account_id", "N/A"),
                'name': account2["name"],
                'thread_id': account2.get('thread_id', 'N/A')
            },
            'reason': reason,
            'region': "SAJEEB" if is_ghost else account1.get('region', 'UNKNOWN'),
            'timestamp': datetime.now().isoformat(),
            'is_ghost': is_ghost
        }
        
        # Gửi bất đồng bộ lên server
        send_couples_account_async(couples_data)
        return True
        
    except Exception as e:
        print_error(f"Error saving couples account: {e}")
        return False

def print_rarity_found(account_data, rarity_type, reason, rarity_score):
    color = Fore.LIGHTMAGENTA_EX
    print(f"\n{color}{Colors.BRIGHT}💎 RARE ACCOUNT FOUND!{Colors.RESET}")
    print(f"{color}🎯 Type: {rarity_type}{Colors.RESET}")
    print(f"{color}⭐ Rarity Score: {rarity_score}{Colors.RESET}")
    print(f"{color}👤 Name: {account_data['name']}{Colors.RESET}")
    print(f"{color}🆔 UID: {account_data['uid']}{Colors.RESET}")
    print(f"{color}🎮 Account ID: {account_data.get('account_id', 'N/A')}{Colors.RESET}")
    print(f"{color}📝 Reason: {reason}{Colors.RESET}")
    print(f"{color}🧵 Thread: {account_data.get('thread_id', 'N/A')}{Colors.RESET}")
    print(f"{color}🌍 Region: {account_data.get('region', 'N/A')}{Colors.RESET}\n")

def print_couples_found(account1, account2, reason):
    color = Fore.LIGHTCYAN_EX
    print(f"\n{color}{Colors.BRIGHT}💑 COUPLES ACCOUNT FOUND!{Colors.RESET}")
    print(f"{color}📝 Reason: {reason}{Colors.RESET}")
    print(f"{color}👤 Account 1: {account1['name']} (ID: {account1.get('account_id', 'N/A')}) - Thread {account1.get('thread_id', 'N/A')}{Colors.RESET}")
    print(f"{color}👤 Account 2: {account2['name']} (ID: {account2.get('account_id', 'N/A')}) - Thread {account2.get('thread_id', 'N/A')}{Colors.RESET}")
    print(f"{color}🆔 UIDs: {account1['uid']} & {account2['uid']}{Colors.RESET}")
    print(f"{color}🌍 Region: {account1.get('region', 'N/A')}{Colors.RESET}\n")

def install_requirements():
    required_packages = [
        'requests',
        'pycryptodome',
        'colorama',
        'urllib3',
        'psutil'
    ]
    
    print(f"{get_random_color()}{Colors.BRIGHT}🔍 Checking required packages...{Colors.RESET}")
    
    for package in required_packages:
        try:
            if package == 'pycryptodome':
                import Crypto
            else:
                importlib.import_module(package)
            print(f"{get_random_color()}✅ {package} is installed{Colors.RESET}")
        except ImportError:
            print(f"{get_random_color()}⚠️ Installing {package}...{Colors.RESET}")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"{get_random_color()}✅ {package} installed successfully{Colors.RESET}")
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}❌ Failed to install {package}{Colors.RESET}")
                return False
    return True

def get_region(language_code: str) -> str:
    return REGION_LANG.get(language_code)

def get_region_url(region_code: str) -> str:
    return REGION_URLS.get(region_code, "https://clientbp.ggblueshark.com/")

def safe_exit(signum=None, frame=None):
    global EXIT_FLAG
    EXIT_FLAG = True
    color = get_random_color()
    print(f"\n{color}{Colors.BRIGHT}🚨 Safe exit triggered. Closing script...{Colors.RESET}")
    sys.exit(0)

signal.signal(signal.SIGINT, safe_exit)
signal.signal(signal.SIGTERM, safe_exit)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    color = get_random_color()
    banner = f"""
{color}{Colors.BRIGHT}
            ‎          ███████╗ ██████╗ 
‎                      ██╔════╝ ██╔══██╗
‎                      ███████╗ ██████╔╝
‎                      ╚════██║ ██╔══██╗
‎                      ███████║ ██████╔╝
‎                     ╚══════╝ ╚═════╝
                
{client_data}
{Colors.RESET}
\n{get_random_color()}{Colors.BRIGHT}🌐 CONNECTED TO SERVER: sg-sgp05.altr.cc:25403{Colors.RESET}
\n{get_random_color()}{Colors.BRIGHT}📤 All accounts will be saved to web server{Colors.RESET}
\n{get_random_color()}{Colors.BRIGHT}Dekho , Isme Sare Accounts Save honge Rare Couple Normal Sb Web Server Pe{Colors.RESET}
\n{get_random_color()}{Colors.BRIGHT}Agar IP ban hota hai to agar wifi use nhi kr rhe tb aeroplane mode on off kro nhi to VPN use kro{Colors.RESET}
\n{get_random_color()}{Colors.BRIGHT}Agr kiska generate nhi ho paa rha to option 11 try kro ghost mode{Colors.RESET}
"""
    print(banner)

def print_success(message):
    color = get_random_color()
    print(f"{color}{Colors.BRIGHT}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Fore.RED}{Colors.BRIGHT}❌ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Fore.YELLOW}{Colors.BRIGHT}⚠️ {message}{Colors.RESET}")

def print_rare(message):
    print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}💎 {message}{Colors.RESET}")

def print_registration_status(count, total, name, uid, password, account_id, region, is_ghost=False):
    print(f"{get_random_color()}{Colors.BRIGHT}📝 Registration {count}/{total}{Colors.RESET}")
    print(f"{get_random_color()}👤 Name: {get_random_color()}{name}{Colors.RESET}")
    print(f"{get_random_color()}🆔 UID: {get_random_color()}{uid}{Colors.RESET}")
    print(f"{get_random_color()}🎮 Account ID: {get_random_color()}{account_id}{Colors.RESET}")
    print(f"{get_random_color()}🔑 Password: {get_random_color()}{password}{Colors.RESET}")
    if is_ghost:
        print(f"{get_random_color()}🌍 Mode: {Fore.LIGHTMAGENTA_EX}GHOST Mode{Colors.RESET}")
    else:
        print(f"{get_random_color()}🌍 Region: {get_random_color()}{region}{Colors.RESET}")
    print()

def generate_exponent_number():
    exponent_digits = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
    number = random.randint(1, 99999)
    number_str = f"{number:05d}"
    exponent_str = ''.join(exponent_digits[digit] for digit in number_str)
    return exponent_str

def generate_random_name(base_name):
    exponent_part = generate_exponent_number()
    return f"{base_name[:7]}{exponent_part}"

def generate_custom_password(prefix):
    garena_decoded = base64.b64decode(GARENA).decode('utf-8')
    characters = string.ascii_uppercase + string.digits
    random_part1 = ''.join(random.choice(characters) for _ in range(5))
    random_part2 = ''.join(random.choice(characters) for _ in range(5))
    return f"{prefix}_{random_part1}_{garena_decoded}_{random_part2}"

def EnC_Vr(N):
    if N < 0: 
        return b''
    H = []
    while True:
        BesTo = N & 0x7F 
        N >>= 7
        if N: 
            BesTo |= 0x80
        H.append(BesTo)
        if not N: 
            break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))           
    return packet

def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    K = AES.new(key , AES.MODE_CBC , iv)
    R = K.encrypt(pad(Z , AES.block_size))
    return R

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def save_jwt_token(account_data, jwt_token, region, is_ghost=False):
    """Lưu JWT token (gửi lên server)"""
    try:
        token_data = {
            'uid': account_data["uid"],
            'account_id': account_data.get("account_id", "N/A"),
            'jwt_token': jwt_token,
            'name': account_data["name"],
            'password': account_data["password"],
            'region': "SAJEEB" if is_ghost else region,
            'thread_id': account_data.get('thread_id', 'N/A'),
            'timestamp': datetime.now().isoformat(),
            'is_ghost': is_ghost
        }
        
        # Gửi bất đồng bộ lên server
        send_token_async(token_data)
        return True
        
    except Exception as e:
        print_error(f"Error saving JWT token: {e}")
        return False

def save_normal_account(account_data, region, is_ghost=False):
    """Lưu account bình thường (gửi lên server)"""
    try:
        # Chuẩn bị data cho web
        web_data = {
            'uid': account_data["uid"],
            'password': account_data["password"],
            'name': account_data["name"],
            'account_id': account_data.get("account_id", "N/A"),
            'region': "SAJEEB" if is_ghost else region,
            'thread_id': account_data.get('thread_id', 'N/A'),
            'is_ghost': is_ghost,
            'timestamp': datetime.now().isoformat(),
            'jwt_token': account_data.get('jwt_token', '')
        }
        
        # Gửi bất đồng bộ lên server
        send_account_async(web_data)
        return True
        
    except Exception as e:
        print_error(f"Error saving normal account: {e}")
        return False

def smart_delay():
    time.sleep(random.uniform(1, 2))

def create_acc(region, account_name, password_prefix, is_ghost=False):
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
        
        response = requests.post(url, headers=headers, data=data, timeout=30, verify=False)
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
        
        response = requests.post(url, headers=headers, data=body, timeout=30, verify=False)
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

def encode_string(original):
    keystream = [0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
                 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30]
    encoded = ""
    for i in range(len(original)):
        orig_byte = ord(original[i])
        key_byte = keystream[i % len(keystream)]
        result_byte = orig_byte ^ key_byte
        encoded += chr(result_byte)
    return {"open_id": original, "field_14": encoded}

def to_unicode_escaped(s):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in s)

def Major_Regsiter(access_token, open_id, field, uid, password, region, account_name, password_prefix, is_ghost=False):
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
        
        response = requests.post(url, headers=headers, data=encrypted_payload, verify=False, timeout=30)
        
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

        response = requests.post(url, headers=headers, data=final_payload, verify=False, timeout=30)
        
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

def decode_jwt_token(jwt_token):
    try:
        parts = jwt_token.split('.')
        if len(parts) >= 2:
            payload_part = parts[1]
            padding = 4 - len(payload_part) % 4
            if padding != 4:
                payload_part += '=' * padding
            decoded = base64.urlsafe_b64decode(payload_part)
            data = json.loads(decoded)
            account_id = data.get('account_id') or data.get('external_id')
            if account_id:
                return str(account_id)
    except Exception as e:
        print_warning(f"JWT decode failed: {e}")
    return "N/A"

def force_region_binding(region, jwt_token):
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
        
        response = requests.post(url, data=payload, headers=headers, verify=False, timeout=30)
        return response.status_code == 200
    except Exception as e:
        print_warning(f"Region binding failed: {e}")
        return False

def generate_single_account(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    global SUCCESS_COUNTER, RARE_COUNTER, COUPLES_COUNTER
    if EXIT_FLAG:
        return None
        
    with LOCK:
        if SUCCESS_COUNTER >= total_accounts:
            return None

    account_result = create_acc(region, account_name, password_prefix, is_ghost)
    if not account_result:
        return None

    account_id = account_result.get("account_id", "N/A")
    jwt_token = account_result.get("jwt_token", "")
    
    account_result['thread_id'] = thread_id

    with LOCK:
        SUCCESS_COUNTER += 1
        current_count = SUCCESS_COUNTER

    print_registration_status(current_count, total_accounts, account_result["name"], 
                            account_result["uid"], account_result["password"], account_id, region, is_ghost)
    
    # Lưu account bình thường lên server
    save_normal_account(account_result, region, is_ghost)
    
    # Kiểm tra và lưu rare account
    is_rare, rarity_type, rarity_reason, rarity_score = check_account_rarity(account_result)
    if is_rare:
        with LOCK:
            RARE_COUNTER += 1
        print_rarity_found(account_result, rarity_type, rarity_reason, rarity_score)
        save_rare_account(account_result, rarity_type, rarity_reason, rarity_score, is_ghost)
        print_success(f"💎 Rare account sent to server! (Total rare: {RARE_COUNTER})")
    
    # Kiểm tra và lưu couples account
    is_couple, couple_reason, partner_data = check_account_couples(account_result, thread_id)
    if is_couple and partner_data:
        with LOCK:
            COUPLES_COUNTER += 1
        print_couples_found(account_result, partner_data, couple_reason)
        save_couples_account(account_result, partner_data, couple_reason, is_ghost)
        print_success(f"💑 Couples accounts sent to server! (Total couples: {COUPLES_COUNTER})")
    
    # Lưu JWT token nếu có
    if jwt_token:
        save_jwt_token(account_result, jwt_token, region, is_ghost)
    
    return {"account": account_result}

def worker(region, account_name, password_prefix, total_accounts, thread_id, is_ghost=False):
    thread_color = get_random_color()
    print(f"{thread_color}{Colors.BRIGHT}🧵 Thread {thread_id} started{Colors.RESET}")
    
    accounts_generated = 0
    while not EXIT_FLAG:
        with LOCK:
            if SUCCESS_COUNTER >= total_accounts:
                break
        
        result = generate_single_account(region, account_name, password_prefix, total_accounts, thread_id, is_ghost)
        if result:
            accounts_generated += 1
        
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"{thread_color}{Colors.BRIGHT}🧵 Thread {thread_id} finished: {accounts_generated} accounts sent to server{Colors.RESET}")

def wait_for_enter():
    print(f"\n{get_random_color()}{Colors.BRIGHT}⏎ Press Enter to continue...{Colors.RESET}")
    input()

def generate_accounts_flow():
    global SUCCESS_COUNTER, TARGET_ACCOUNTS, RARE_COUNTER, COUPLES_COUNTER, RARITY_SCORE_THRESHOLD
    
    # Kiểm tra kết nối server trước
    print(f"\n{get_random_color()}{Colors.BRIGHT}🔗 Checking server connection...{Colors.RESET}")
    if not WEB_SAVER.check_connection():
        print_warning("⚠️ Cannot connect to server.")
        print_warning("Accounts cannot be saved without server connection.")
        response = input(f"{Fore.YELLOW}Exit and try again? (y/n): {Style.RESET_ALL}").lower()
        if response != 'n':
            return
    
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
                return
            elif choice == "000":
                print(f"\n{get_random_color()}{Colors.BRIGHT}👋 Thank you for using SAJEEB Generator!{Colors.RESET}")
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
            safe_exit()

    clear_screen()
    display_banner()
    
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
            rarity_threshold = int(input(f"\n{get_random_color()}{Colors.BRIGHT}⭐ Rarity Threshold (default 2): {Colors.RESET}"))
            if 1 <= rarity_threshold <= 10:
                RARITY_SCORE_THRESHOLD = rarity_threshold
                break
            else:
                print_error("Please enter a number between 1 and 10.")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
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
            safe_exit()

    clear_screen()
    display_banner()
    
    if is_ghost:
        print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}🚀 Starting GHOST MODE Account Generation{Colors.RESET}")
    else:
        print(f"{get_random_color()}{Colors.BRIGHT}🚀 Starting Account Generation for {selected_region}{Colors.RESET}")
    
    print(f"{get_random_color()}{Colors.BRIGHT}🎯 Target Accounts: {account_count}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}👤 Name Prefix: {account_name}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}🔑 Password Prefix: {password_prefix}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}⭐ Rarity Threshold: {RARITY_SCORE_THRESHOLD}+{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}🧵 Threads: {thread_count}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}🌐 Server: sg-sgp05.altr.cc:25403{Colors.RESET}")
    print(f"\n{get_random_color()}{Colors.BRIGHT}⏳ Starting in 3 seconds...{Colors.RESET}")
    time.sleep(3)

    SUCCESS_COUNTER = 0
    TARGET_ACCOUNTS = account_count
    RARE_COUNTER = 0
    COUPLES_COUNTER = 0
    start_time = time.time()
    threads = []

    print(f"\n{get_random_color()}{Colors.BRIGHT}🚀 Starting generation with {thread_count} threads...{Colors.RESET}\n")

    for i in range(thread_count):
        t = threading.Thread(target=worker, args=(selected_region, account_name, password_prefix, account_count, i+1, is_ghost))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(2)
            with LOCK:
                current_count = SUCCESS_COUNTER
            progress = (current_count / account_count) * 100
            print(f"{get_random_color()}{Colors.BRIGHT}📊 Progress: {current_count}/{account_count} ({progress:.1f}%) | 💎 Rare: {RARE_COUNTER} | 💑 Couples: {COUPLES_COUNTER}{Colors.RESET}")
            if current_count >= account_count:
                break
                
    except KeyboardInterrupt:
        print_warning("Generation interrupted by user!")
        EXIT_FLAG = True
        for t in threads:
            t.join(timeout=1)

    for t in threads:
        t.join(timeout=5)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n{get_random_color()}{Colors.BRIGHT}🎉 Generation completed!{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}📊 Accounts sent to server: {SUCCESS_COUNTER}/{account_count}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}💎 Rare accounts found: {RARE_COUNTER}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}💑 Couples pairs found: {COUPLES_COUNTER}{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}⭐ Rarity threshold used: {RARITY_SCORE_THRESHOLD}+{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}⏱️ Time taken: {elapsed_time:.2f} seconds{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}⚡ Speed: {SUCCESS_COUNTER/elapsed_time:.2f} accounts/second{Colors.RESET}")
    print(f"{get_random_color()}{Colors.BRIGHT}🌐 All accounts saved to: sg-sgp05.altr.cc:25403{Colors.RESET}")
    
    # Lấy stats từ server
    try:
        stats = WEB_SAVER.get_stats()
        if stats:
            print(f"\n{Fore.CYAN}{Colors.BRIGHT}📈 SERVER STATS:{Colors.RESET}")
            print(f"{Fore.CYAN}📊 Total accounts on server: {stats.get('total_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}💎 Rare accounts on server: {stats.get('total_rare_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}💑 Couples on server: {stats.get('total_couples_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}🔐 Tokens on server: {stats.get('total_tokens', 0)}{Colors.RESET}")
    except:
        pass
    
    print(f"\n{get_random_color()}{Colors.BRIGHT}Press Enter to Continue...{Colors.RESET}")
    wait_for_enter()

def view_server_stats():
    """Xem thống kê từ server"""
    clear_screen()
    display_banner()
    
    print(f"{get_random_color()}{Colors.BRIGHT}📊 Viewing Server Stats{Colors.RESET}")
    
    try:
        stats = WEB_SAVER.get_stats()
        if stats:
            print(f"\n{Fore.CYAN}{Colors.BRIGHT}🌐 Server: {stats.get('server', 'Unknown')}{Colors.RESET}")
            print(f"{Fore.CYAN}🕒 Last Updated: {stats.get('timestamp', 'Unknown')}{Colors.RESET}")
            print(f"{Fore.CYAN}📊 Total Accounts: {stats.get('total_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}💎 Rare Accounts: {stats.get('total_rare_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}💑 Couples Accounts: {stats.get('total_couples_accounts', 0)}{Colors.RESET}")
            print(f"{Fore.CYAN}🔐 Tokens: {stats.get('total_tokens', 0)}{Colors.RESET}")
            
            print(f"\n{Fore.YELLOW}{Colors.BRIGHT}🌍 Accounts by Region:{Colors.RESET}")
            regions = stats.get('regions', {})
            if regions:
                for region, count in regions.items():
                    print(f"  {region}: {count}")
            else:
                print("  No region data")
            
            print(f"\n{Fore.GREEN}{Colors.BRIGHT}💾 Storage:{Colors.RESET}")
            storage = stats.get('storage', {})
            print(f"  Total Size: {storage.get('total_files_mb', 0)} MB")
            print(f"  Main File: {storage.get('main_file_mb', 0)} MB")
            
            print(f"\n{Fore.MAGENTA}{Colors.BRIGHT}⚡ Performance:{Colors.RESET}")
            perf = stats.get('performance', {})
            print(f"  Uptime: {perf.get('uptime', 'Unknown')}")
            print(f"  Total Requests: {perf.get('total_requests', 0)}")
            print(f"  Accounts/Minute: {perf.get('accounts_per_minute', 0)}")
        else:
            print(f"\n{Fore.RED}❌ Could not fetch stats from server{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error fetching stats: {e}{Style.RESET_ALL}")
    
    wait_for_enter()

def about_section():
    clear_screen()
    display_banner()
    
    print(f"{get_random_color()}{Colors.BRIGHT}ℹ️  About SAJEEB Account Generator{Colors.RESET}")
    print(f"\n{get_random_color()}{Colors.BRIGHT}✨ Features:{Colors.RESET}")
    print(f"{get_random_color()}• Generate Free Fire accounts for multiple regions{Colors.RESET}")
    print(f"{get_random_color()}• GHOST Mode for special accounts{Colors.RESET}")
    print(f"{get_random_color()}• All accounts saved to web server{Colors.RESET}")
    print(f"{get_random_color()}• Automatic JWT token generation{Colors.RESET}")
    print(f"{get_random_color()}• Multi-threaded generation{Colors.RESET}")
    print(f"{get_random_color()}• Rare account detection{Colors.RESET}")
    print(f"{get_random_color()}• Couples account matching{Colors.RESET}")
    
    print(f"\n{get_random_color()}{Colors.BRIGHT}🌐 Web Server:{Colors.RESET}")
    print(f"{get_random_color()}• Server: sg-sgp05.altr.cc:25403{Colors.RESET}")
    print(f"{get_random_color()}• All data saved to single JSON file{Colors.RESET}")
    print(f"{get_random_color()}• Real-time statistics{Colors.RESET}")
    
    print(f"\n{get_random_color()}{Colors.BRIGHT}⚠️  Disclaimer:{Colors.RESET}")
    print(f"{get_random_color()}This tool is for educational purposes only.{Colors.RESET}")
    print(f"{get_random_color()}Use at your own risk.{Colors.RESET}")
    
    wait_for_enter()

def main_menu():
    while True:
        clear_screen()
        display_banner()
        
        print(f"{get_random_color()}{Colors.BRIGHT}🎮 Welcome to SAJEEB Account Generator{Colors.RESET}")
        print(f"\n{get_random_color()}{Colors.BRIGHT}📋 Available Options:{Colors.RESET}")
        print(f"{get_random_color()}1) {get_random_color()}Generate Accounts{Colors.RESET}")
        print(f"{get_random_color()}2) {get_random_color()}View Server Stats{Colors.RESET}")
        print(f"{get_random_color()}3) {get_random_color()}About{Colors.RESET}")
        print(f"{get_random_color()}0) {Fore.RED}Exit{Colors.RESET}")

        try:
            choice = input(f"\n{get_random_color()}{Colors.BRIGHT}🎯 Choose option: {Colors.RESET}").strip()
            
            if choice == "1":
                generate_accounts_flow()
            elif choice == "2":
                view_server_stats()
            elif choice == "3":
                about_section()
            elif choice == "0":
                print(f"\n{get_random_color()}{Colors.BRIGHT}👋 Thank you for using SAJEEB Generator!{Colors.RESET}")
                sys.exit(0)
            else:
                print_error("Invalid option. Please choose 1, 2, 3, or 0.")
                time.sleep(1)
        except KeyboardInterrupt:
            safe_exit()

if __name__ == "__main__":
    try:
        if install_requirements():
            print(f"\n{Fore.GREEN}✅ All requirements installed{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🔗 Checking server connection...{Style.RESET_ALL}")
            if WEB_SAVER.check_connection():
                print(f"{Fore.GREEN}✅ Ready to generate accounts!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Cannot connect to server. Please check:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  1. Server is running on sg-sgp05.altr.cc:25403{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  2. Network connection is working{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  3. Port 25403 is accessible{Style.RESET_ALL}")
                response = input(f"\n{Fore.YELLOW}Continue anyway? (y/n): {Style.RESET_ALL}").lower()
                if response != 'y':
                    sys.exit(1)
            time.sleep(2)
            main_menu()
    except KeyboardInterrupt:
        safe_exit()
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        traceback.print_exc()
        print(f"\n{Fore.YELLOW}{Colors.BRIGHT}🔄 Restarting script...{Colors.RESET}")
        time.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
