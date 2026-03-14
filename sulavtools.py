#!/usr/bin/env python3
"""
SulavXMRC Multi‑Purpose Bot – ULTIMATE EDITION with Quiz System
All features integrated: Guild, Friend, Long Bio, Guest Generator, Token Tools,
Player Info, Ban Check, Event Info, JWT Generator, Wallet, Daily Bonus, Referrals,
Redeem Codes, Admin Panel, Maintenance Mode, Leaderboard, Daily Top Rewards,
and Daily Quiz System with 5 questions (Maths, GK, Science).

Author: Spideerio (customized for user)
"""

import os
import sys
import json
import logging
import sqlite3
import random
import string
from datetime import datetime, date, timedelta, time
from functools import wraps
from typing import Optional, Dict, List, Tuple, Union
import asyncio

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    JobQueue,
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import TelegramError
from telegram.helpers import escape_markdown

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8739803908:AAEHiLmGcCaFgZ5qL1QeDQjr1MMaTWx_zYI"
ADMIN_IDS = [5938491424]
DATABASE_FILE = "danger_bot.db"

# API Base URLs
FRIEND_MANAGER_BASE = "https://danger-friend-management.vercel.app"
GUILD_MANAGER_BASE = "https://guild-info-danger.vercel.app"
LONG_BIO_API = "https://sulav-long-bio-api-five.vercel.app/bio_upload"
GUEST_GEN_API = "https://sulav-new-guest-api.vercel.app/gen"
JWT_API = "https://sulav-jwt-token.vercel.app/token"
PLAYER_INFO_API = "https://free-fire-api--tsandesh756.replit.app/get_player_personal_show"
BAN_CHECK_API = "https://flash-ban-check.vercel.app/bancheck"
EVENT_INFO_API = "https://danger-event-info.vercel.app/event"
ACCESS_TOKEN_API = "http://danger-access-token.vercel.app"

# Coin costs
COST_JWT_GEN = 10
COST_PLAYER_INFO = 5
COST_BAN_CHECK = 5
COST_EVENT_INFO = 10
COST_ACCESS_TO_JWT = 5
COST_EAT_TO_ACCESS = 5
COST_EAT_TO_JWT = 8
COST_SEND_FRIEND_REQUEST = 5
COST_GUEST_PER_ACCOUNT = 5

# Quiz settings
QUIZ_REWARD_CORRECT = 5
QUIZ_PENALTY_WRONG = 5
QUIZ_QUESTIONS_PER_DAY = 5
QUIZ_TIME_LIMIT = 30  # seconds per question

# Daily reward for top users
TOP_REWARD_AMOUNT = 20
TOP_REWARD_COUNT = 3

# Maintenance message
MAINTENANCE_MESSAGE = (
    "⚠️ *Bot Temporarily Unavailable*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ Due to a high volume of purchase requests, our system is currently processing previous orders.\n\n"
    "We apologize for the inconvenience and appreciate your patience.\n\n"
    "You will be notified automatically once the bot is available again.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "Thank you for your understanding. 🙏"
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Conversation states
REGION, NAME, COUNT = range(3)  # for guest generator
(FRIEND_ACTION, FRIEND_UID, FRIEND_PASSWORD, FRIEND_TARGET) = range(10, 14)  # for friend management
QUIZ_ACTIVE = range(20, 21)  # for quiz

# ==================== QUIZ QUESTIONS DATABASE ====================
QUIZ_QUESTIONS = [
    # Maths
    {
        "question": "What is 15 × 12?",
        "options": ["150", "160", "170", "180"],
        "correct": 3,
        "category": "Maths"
    },
    {
        "question": "What is the square root of 144?",
        "options": ["10", "11", "12", "13"],
        "correct": 2,
        "category": "Maths"
    },
    {
        "question": "If x + 5 = 12, what is x?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,
        "category": "Maths"
    },
    {
        "question": "What is 25% of 200?",
        "options": ["25", "40", "50", "60"],
        "correct": 2,
        "category": "Maths"
    },
    {
        "question": "What is 7! (7 factorial)?",
        "options": ["5040", "720", "120", "504"],
        "correct": 0,
        "category": "Maths"
    },
    {
        "question": "What is the value of π (pi) to two decimal places?",
        "options": ["3.14", "3.16", "3.12", "3.18"],
        "correct": 0,
        "category": "Maths"
    },
    {
        "question": "Solve: 3² + 4² = ?",
        "options": ["7", "12", "25", "16"],
        "correct": 2,
        "category": "Maths"
    },
    
    # General Knowledge
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2,
        "category": "GK"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "correct": 1,
        "category": "GK"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "correct": 3,
        "category": "GK"
    },
    {
        "question": "In which year did World War II end?",
        "options": ["1944", "1945", "1946", "1947"],
        "correct": 1,
        "category": "GK"
    },
    {
        "question": "What is the longest river in the world?",
        "options": ["Amazon", "Nile", "Yangtze", "Mississippi"],
        "correct": 1,
        "category": "GK"
    },
    {
        "question": "Who was the first man to step on the moon?",
        "options": ["Buzz Aldrin", "Yuri Gagarin", "Neil Armstrong", "Michael Collins"],
        "correct": 2,
        "category": "GK"
    },
    {
        "question": "What is the national animal of India?",
        "options": ["Lion", "Tiger", "Elephant", "Peacock"],
        "correct": 1,
        "category": "GK"
    },
    
    # Science
    {
        "question": "What is the chemical symbol for gold?",
        "options": ["Go", "Gd", "Au", "Ag"],
        "correct": 2,
        "category": "Science"
    },
    {
        "question": "How many bones are in the adult human body?",
        "options": ["206", "205", "208", "210"],
        "correct": 0,
        "category": "Science"
    },
    {
        "question": "What planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": 1,
        "category": "Science"
    },
    {
        "question": "What is the hardest natural substance on Earth?",
        "options": ["Gold", "Iron", "Diamond", "Platinum"],
        "correct": 2,
        "category": "Science"
    },
    {
        "question": "What is the boiling point of water at sea level?",
        "options": ["90°C", "100°C", "110°C", "120°C"],
        "correct": 1,
        "category": "Science"
    },
    {
        "question": "What is the speed of light in vacuum?",
        "options": ["300,000 km/s", "150,000 km/s", "400,000 km/s", "200,000 km/s"],
        "correct": 0,
        "category": "Science"
    },
    {
        "question": "What is the largest organ in the human body?",
        "options": ["Heart", "Liver", "Skin", "Brain"],
        "correct": 2,
        "category": "Science"
    },
]

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        coins INTEGER DEFAULT 0,
        referral_code TEXT UNIQUE,
        referred_by INTEGER,
        daily_bonus_date TEXT,
        total_referrals INTEGER DEFAULT 0,
        quiz_score INTEGER DEFAULT 0,
        quiz_questions_answered INTEGER DEFAULT 0,
        quiz_last_played TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add missing columns for ban system
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN banned_until TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN quiz_score INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN quiz_questions_answered INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN quiz_last_played TEXT")
    except sqlite3.OperationalError:
        pass
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        type TEXT,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Redeem codes table
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        coins INTEGER,
        max_uses INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0,
        created_by INTEGER,
        expires_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Referrals table
    c.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        reward_claimed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Ban log table
    c.execute('''CREATE TABLE IF NOT EXISTS ban_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        admin_id INTEGER,
        reason TEXT,
        banned_until TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Quiz history table
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        answer INTEGER,
        correct INTEGER,
        coins_earned INTEGER,
        played_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Settings table
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_min', '10')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_max', '50')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', '0')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('reward_hour', '0')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('reward_minute', '0')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('quiz_questions_per_day', '5')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('quiz_reward_correct', '5')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('quiz_penalty_wrong', '5')")
    
    conn.commit()
    conn.close()
    logger.info("Database initialized/upgraded.")

# ==================== DATABASE HELPER FUNCTIONS ====================
def get_user(user_id: int) -> Optional[Dict]:
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in c.fetchall()]
        conn.close()
        return dict(zip(columns, row))
    return None

def create_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    ref_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    c.execute(
        """INSERT OR IGNORE INTO users 
        (user_id, username, first_name, last_name, referral_code) 
        VALUES (?, ?, ?, ?, ?)""",
        (user_id, username, first_name, last_name, ref_code),
    )
    conn.commit()
    conn.close()

def update_last_active(user_id: int):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_coins(user_id: int, amount: int, description: str = ""):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    c.execute(
        "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, 'earn', ?)",
        (user_id, amount, description),
    )
    conn.commit()
    conn.close()

def deduct_coins(user_id: int, amount: int, description: str = "") -> bool:
    user = get_user(user_id)
    if not user or user["coins"] < amount:
        return False
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, user_id))
    c.execute(
        "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, 'spend', ?)",
        (user_id, amount, description),
    )
    conn.commit()
    conn.close()
    return True

def get_transactions(user_id: int, limit: int = 5) -> List[Dict]:
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        """SELECT amount, type, description, created_at 
           FROM transactions WHERE user_id = ? 
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, limit),
    )
    rows = c.fetchall()
    conn.close()
    return [{"amount": r[0], "type": r[1], "description": r[2], "created_at": r[3]} for r in rows]

def generate_referral_code(user_id: int) -> str:
    user = get_user(user_id)
    return user["referral_code"] if user else ""

def process_referral(referred_id: int, referrer_code: str) -> bool:
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE referral_code = ?", (referrer_code,))
    row = c.fetchone()
    if not row or row[0] == referred_id:
        conn.close()
        return False
    referrer_id = row[0]
    c.execute("SELECT id FROM referrals WHERE referred_id = ?", (referred_id,))
    if c.fetchone():
        conn.close()
        return False
    c.execute(
        "INSERT INTO referrals (referrer_id, referred_id, reward_claimed) VALUES (?, ?, 0)",
        (referrer_id, referred_id),
    )
    c.execute("UPDATE users SET total_referrals = total_referrals + 1 WHERE user_id = ?", (referrer_id,))
    conn.commit()
    conn.close()
    return True

def is_user_banned(user_id: int) -> Tuple[bool, Optional[str]]:
    user = get_user(user_id)
    if not user:
        return False, None
    if user.get("is_banned", 0):
        banned_until = user.get("banned_until")
        if banned_until:
            try:
                until = datetime.fromisoformat(banned_until)
                if datetime.now() > until:
                    unban_user(user_id)
                    return False, None
                return True, f"Banned until {until.strftime('%Y-%m-%d %H:%M')}"
            except:
                return True, "Banned permanently"
        return True, "Banned permanently"
    return False, None

def ban_user(user_id: int, admin_id: int, reason: str = "", duration_hours: Optional[int] = None):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    banned_until = None
    if duration_hours:
        banned_until = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
    c.execute("UPDATE users SET is_banned = 1, banned_until = ? WHERE user_id = ?", (banned_until, user_id))
    c.execute(
        "INSERT INTO ban_log (user_id, admin_id, reason, banned_until) VALUES (?, ?, ?, ?)",
        (user_id, admin_id, reason, banned_until)
    )
    conn.commit()
    conn.close()

def unban_user(user_id: int):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0, banned_until = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None) -> str:
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def is_maintenance() -> bool:
    return get_setting("maintenance", "0") == "1"

# ==================== QUIZ FUNCTIONS ====================
def can_play_quiz(user_id: int) -> Tuple[bool, int, int]:
    """Check if user can play quiz today. Returns (can_play, questions_answered, total_questions)"""
    user = get_user(user_id)
    if not user:
        return False, 0, 0
    
    today = date.today().isoformat()
    last_played = user.get("quiz_last_played", "")
    questions_answered = user.get("quiz_questions_answered", 0)
    max_questions = int(get_setting("quiz_questions_per_day", "5"))
    
    if last_played != today:
        # New day, reset counter
        return True, 0, max_questions
    else:
        return questions_answered < max_questions, questions_answered, max_questions

def get_random_question() -> Dict:
    """Get a random quiz question."""
    return random.choice(QUIZ_QUESTIONS)

def record_quiz_answer(user_id: int, question: Dict, answer_index: int, correct: bool, coins_earned: int):
    """Record quiz answer in history and update user stats."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Update user stats
    today = date.today().isoformat()
    questions_answered = c.execute(
        "SELECT quiz_questions_answered FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    
    c.execute(
        """UPDATE users SET 
           quiz_questions_answered = ?, 
           quiz_last_played = ?,
           quiz_score = quiz_score + ? 
           WHERE user_id = ?""",
        (questions_answered + 1, today, 1 if correct else 0, user_id)
    )
    
    # Insert history
    c.execute(
        """INSERT INTO quiz_history 
           (user_id, question, answer, correct, coins_earned) 
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, question['question'], answer_index, 1 if correct else 0, coins_earned)
    )
    
    conn.commit()
    conn.close()

def get_quiz_stats(user_id: int) -> Dict:
    """Get quiz statistics for a user."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # Get user stats
    c.execute("SELECT quiz_score, quiz_questions_answered FROM users WHERE user_id = ?", (user_id,))
    user_stats = c.fetchone()
    
    # Get today's stats
    today = date.today().isoformat()
    c.execute(
        """SELECT COUNT(*), SUM(coins_earned) FROM quiz_history 
           WHERE user_id = ? AND date(played_at) = ?""",
        (user_id, today)
    )
    today_stats = c.fetchone()
    
    conn.close()
    
    return {
        "total_score": user_stats[0] if user_stats else 0,
        "total_questions": user_stats[1] if user_stats else 0,
        "today_questions": today_stats[0] if today_stats[0] else 0,
        "today_earnings": today_stats[1] if today_stats[1] else 0
    }

# ==================== LEADERBOARD FUNCTIONS ====================
def get_top_users(limit: int = 10) -> List[Dict]:
    """Get top users by coins (excluding banned users)."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT user_id, username, first_name, coins FROM users WHERE is_banned = 0 ORDER BY coins DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"user_id": r[0], "username": r[1], "first_name": r[2], "coins": r[3]} for r in rows]

def get_quiz_leaderboard(limit: int = 10) -> List[Dict]:
    """Get top users by quiz score."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT user_id, username, first_name, quiz_score FROM users WHERE is_banned = 0 ORDER BY quiz_score DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"user_id": r[0], "username": r[1], "first_name": r[2], "score": r[3]} for r in rows]

def reset_all_coins():
    """Set all users' coins to 0 (admin only)."""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET coins = 0")
    conn.commit()
    conn.close()

def give_daily_top_rewards():
    """Give reward to top N users."""
    top_users = get_top_users(TOP_REWARD_COUNT)
    for user in top_users:
        add_coins(user["user_id"], TOP_REWARD_AMOUNT, f"Daily top {TOP_REWARD_COUNT} reward")
    logger.info(f"Daily rewards given to top {len(top_users)} users: {[u['user_id'] for u in top_users]}")
    return top_users

# ==================== API CALL FUNCTIONS (SMART FORMATTING) ====================
def call_friend_api(endpoint: str, params: dict) -> Tuple[bool, Union[dict, str]]:
    url = f"{FRIEND_MANAGER_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            try:
                return True, resp.json()
            except:
                return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def call_guild_api(endpoint: str, params: dict) -> Tuple[bool, Union[dict, str]]:
    url = f"{GUILD_MANAGER_BASE}/{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            try:
                return True, resp.json()
            except:
                return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def update_long_bio(uid: str = None, password: str = None, access_token: str = None, bio: str = None) -> Tuple[bool, str]:
    params = {}
    if uid and password:
        params["uid"] = uid
        params["pass"] = password
    elif access_token:
        params["access"] = access_token
    else:
        return False, "Missing credentials"
    params["bio"] = bio
    try:
        resp = requests.get(LONG_BIO_API, params=params, timeout=30)
        if resp.status_code == 200:
            return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_guest(name: str, count: int, region: str) -> Tuple[bool, Union[dict, str]]:
    params = {"name": name, "count": count, "region": region}
    try:
        resp = requests.get(GUEST_GEN_API, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return True, data
            else:
                return False, data
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def generate_jwt(uid: str, password: str) -> Tuple[bool, Union[dict, str]]:
    url = f"{JWT_API}?uid={uid}&password={password}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict) and data.get("error"):
                    return False, data.get("error")
                return True, data
            except:
                return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def get_player_info(uid: str, region: str) -> Tuple[bool, Union[dict, str]]:
    url = f"{PLAYER_INFO_API}?server={region}&uid={uid}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict) and data.get("error"):
                    return False, data.get("error")
                return True, data
            except:
                return True, resp.text
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def check_ban(uid: str) -> Tuple[bool, Union[dict, str]]:
    url = f"{BAN_CHECK_API}?uid={uid}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def get_event_info(region: str) -> Tuple[bool, Union[dict, str]]:
    """Fetch event info with better error handling."""
    url = f"{EVENT_INFO_API}?region={region}&key=DANGERxEVENT"
    try:
        logger.info(f"Fetching event info for region: {region}")
        resp = requests.get(url, timeout=30)
        logger.info(f"Event API response status: {resp.status_code}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                return True, data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from event API: {e}")
                return True, resp.text
        else:
            error_msg = f"HTTP {resp.status_code}"
            try:
                error_data = resp.json()
                if isinstance(error_data, dict) and error_data.get('error'):
                    error_msg = error_data.get('error')
            except:
                error_msg = resp.text[:200] if resp.text else error_msg
            return False, f"❌ API Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching event info for region {region}")
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching event info: {e}")
        return False, "❌ Could not connect to the event server. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error in get_event_info: {e}", exc_info=True)
        return False, f"❌ Unexpected error: {str(e)[:100]}"

def access_to_jwt(access_token: str) -> Tuple[bool, Union[dict, str]]:
    url = f"{ACCESS_TOKEN_API}/access-to-jwt?access_token={access_token}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def eat_to_access(eat_token: str) -> Tuple[bool, Union[dict, str]]:
    url = f"{ACCESS_TOKEN_API}/eat-to-access?eat_token={eat_token}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, f"HTTP {resp.status_code}: {resp.text}"
    except requests.exceptions.Timeout:
        return False, "⏳ Request timed out. The server is slow, please try again later."
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

def eat_to_jwt(eat_token: str) -> Tuple[bool, Union[dict, str]]:
    success, access_result = eat_to_access(eat_token)
    if not success:
        return False, access_result
    if isinstance(access_result, dict) and 'access_token' in access_result:
        return access_to_jwt(access_result['access_token'])
    else:
        return False, "Failed to extract access token from EAT"

# ==================== HELPER: SEND LONG TEXT AS FILE ====================
async def send_long_text(update: Update, text: str, filename: str = "output.txt", caption: str = None):
    """Send long text as a file if too long, otherwise as a normal message."""
    MAX_LENGTH = 3500  # Telegram message limit is 4096, we leave some margin
    if len(text) <= MAX_LENGTH:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        # Write to temporary file and send as document
        filepath = f"/tmp/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        with open(filepath, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption=caption or f"📄 Result (too long to display)"
            )
        os.remove(filepath)

# ==================== DECORATORS ====================
def require_user(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user:
            return
        if is_maintenance():
            if update.message and update.message.text and update.message.text.startswith('/maintenance'):
                if user.id in ADMIN_IDS:
                    return await func(update, context, *args, **kwargs)
            await update.message.reply_text(MAINTENANCE_MESSAGE, parse_mode=ParseMode.MARKDOWN)
            return
        create_user(user.id, user.username, user.first_name, user.last_name)
        update_last_active(user.id)
        banned, reason = is_user_banned(user.id)
        if banned:
            await update.message.reply_text(f"⛔ You are banned. {reason}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ Unauthorized. This command is for admins only.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ==================== USER COMMAND HANDLERS ====================
@require_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args and len(context.args) > 0:
        process_referral(user.id, context.args[0])
    full_name = escape_markdown(" ".join(filter(None, [user.first_name, user.last_name])) or "User")
    user_id_escaped = escape_markdown(str(user.id))
    username_escaped = escape_markdown(f"@{user.username}") if user.username else ""
    welcome_text = (
        f"🎮 *Welcome, {full_name}!*\n\n"
        f"🆔 Your ID: `{user_id_escaped}`\n"
    )
    if username_escaped:
        welcome_text += f"📛 Username: {username_escaped}\n"
    welcome_text += "\nUse the menu below to access features.\nUse /help for commands."
    
    keyboard = [
        ["🛡️ Guild", "👥 Friend"],
        ["📝 Long Bio", "🎫 Guest Gen"],
        ["🔧 Token Tools", "ℹ️ Player Info"],
        ["🚫 Ban Check", "🎉 Event Info"],
        ["📦 Jwt Gen", "👤 Wallet"],
        ["💰 Daily", "🎁 Refer"],
        ["🏆 Redeem", "🏅 Leaderboard"],
        ["📊 Quiz", "📈 Quiz Stats"]  # New quiz buttons
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    try:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await update.message.reply_photo(
                photo=file_id, caption=welcome_text,
                parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Failed to send profile photo: {e}")
        await update.message.reply_text(
            welcome_text.replace('*', '').replace('`', ''),
            parse_mode=None, reply_markup=reply_markup
        )

@require_user
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 *Available Commands*\n\n"
        "/start - Main menu\n"
        "/wallet - Check your coin balance\n"
        "/daily - Claim daily bonus\n"
        "/refer - Get your referral link\n"
        "/redeem <code> - Redeem a code\n"
        "/setuid <UID> <PASSWORD> - Save credentials temporarily\n"
        "/leaderboard - View top coin holders\n"
        "/quiz - Start daily quiz (5 questions)\n"
        "/quizstats - View your quiz statistics\n"
        "/quizlb - View quiz leaderboard\n"
        "/admin - Open admin panel (admins only)\n\n"
        "Use the buttons to access all features."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@require_user
async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found.")
        return
    transactions = get_transactions(user_id, 5)
    trans_text = ""
    for t in transactions:
        symbol = "➕" if t["type"] == "earn" else "➖"
        trans_text += f"\n{symbol} {escape_markdown(t['description'])}: {t['amount']} coins"
    balance_escaped = escape_markdown(str(user['coins']))
    text = (
        f"👤 *Your Wallet*\n\n"
        f"💰 Balance: `{balance_escaped}` coins\n"
        f"📊 Total Referrals: {user['total_referrals']}\n"
        f"📚 Quiz Score: {user.get('quiz_score', 0)}\n\n"
        f"📈 *Recent Transactions:*{trans_text}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@require_user
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    today = date.today().isoformat()
    if user["daily_bonus_date"] == today:
        await update.message.reply_text("❌ You've already claimed today's bonus!")
        return
    daily_min = int(get_setting("daily_min", "10"))
    daily_max = int(get_setting("daily_max", "50"))
    bonus = random.randint(daily_min, daily_max)
    add_coins(user_id, bonus, "Daily bonus")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET daily_bonus_date = ? WHERE user_id = ?", (today, user_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🎉 Daily Bonus: +{bonus} coins!\nCome back tomorrow for more!")

@require_user
async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_code = generate_referral_code(user_id)
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={ref_code}"
    total_refs = get_user(user_id)['total_referrals']
    
    md_message = (
        "🎁 *Refer & Earn*\n\n"
        "Share this link with your friends. You'll get **20 coins** for each friend who joins!\n\n"
        f"🔗 {link}\n\n"
        f"Your referral code: `{ref_code}`\n"
        f"Total referrals: {total_refs}"
    )
    plain_message = (
        "🎁 Refer & Earn\n\n"
        "Share this link with your friends. You'll get 20 coins for each friend who joins!\n\n"
        f"Link: {link}\n\n"
        f"Your referral code: {ref_code}\n"
        f"Total referrals: {total_refs}"
    )
    
    try:
        await update.message.reply_text(md_message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Refer command Markdown failed: {e}")
        await update.message.reply_text(plain_message)

@require_user
async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /redeem <CODE>")
        return
    code = context.args[0].upper()
    user_id = update.effective_user.id
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        """SELECT coins, max_uses, used_count FROM redeem_codes 
           WHERE code = ? AND (expires_at IS NULL OR expires_at > datetime('now'))""",
        (code,)
    )
    row = c.fetchone()
    if not row:
        await update.message.reply_text("❌ Invalid or expired code.")
        conn.close()
        return
    coins, max_uses, used_count = row
    if used_count >= max_uses:
        await update.message.reply_text("❌ This code has reached its maximum uses.")
        conn.close()
        return
    c.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    add_coins(user_id, coins, f"Redeemed code {code}")
    await update.message.reply_text(f"✅ Success! You received {coins} coins.")

@require_user
async def setuid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /setuid <UID> <PASSWORD>")
        return
    uid, password = context.args
    context.user_data["saved_uid"] = uid
    context.user_data["saved_password"] = password
    await update.message.reply_text("✅ Credentials saved temporarily for this session.")

@require_user
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top users by coins."""
    top_users = get_top_users(10)
    if not top_users:
        await update.message.reply_text("No users found.")
        return
    text = "🏆 *Leaderboard – Top 10 Richest Players*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        name = user['first_name'] or f"User{user['user_id']}"
        if user['username']:
            name += f" (@{user['username']})"
        coins = user['coins']
        text += f"{medal} {escape_markdown(name)} – `{coins}` coins\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@require_user
async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the daily quiz."""
    user_id = update.effective_user.id
    
    # Check if user can play
    can_play, answered, total = can_play_quiz(user_id)
    if not can_play:
        await update.message.reply_text(
            f"❌ You've already completed all {total} questions for today!\n"
            f"Come back tomorrow for more questions."
        )
        return
    
    # Initialize quiz session
    context.user_data['quiz_questions'] = []
    context.user_data['quiz_current'] = 0
    context.user_data['quiz_correct'] = 0
    context.user_data['quiz_total'] = total
    
    # Generate questions for this session
    for _ in range(total - answered):
        context.user_data['quiz_questions'].append(get_random_question())
    
    await update.message.reply_text(
        f"📊 *Daily Quiz Started!*\n\n"
        f"You have {total - answered} questions remaining today.\n"
        f"✅ Correct: +{QUIZ_REWARD_CORRECT} coins\n"
        f"❌ Wrong: -{QUIZ_PENALTY_WRONG} coins\n"
        f"⏱️ You have {QUIZ_TIME_LIMIT} seconds per question.\n\n"
        f"Let's begin!"
    )
    
    # Send first question
    await send_quiz_question(update, context)
    return QUIZ_ACTIVE

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the next quiz question."""
    current = context.user_data['quiz_current']
    questions = context.user_data['quiz_questions']
    
    if current >= len(questions):
        # Quiz finished
        correct = context.user_data['quiz_correct']
        total = len(questions)
        earned = correct * QUIZ_REWARD_CORRECT
        penalty = (total - correct) * QUIZ_PENALTY_WRONG
        net = earned - penalty
        
        if net > 0:
            add_coins(update.effective_user.id, net, f"Quiz earnings: {correct}/{total} correct")
        elif net < 0:
            deduct_coins(update.effective_user.id, -net, f"Quiz penalty: {correct}/{total} correct")
        
        stats = get_quiz_stats(update.effective_user.id)
        await update.message.reply_text(
            f"🎉 *Quiz Completed!*\n\n"
            f"📊 Results:\n"
            f"✅ Correct: {correct}/{total}\n"
            f"💰 Net change: {net:+d} coins\n\n"
            f"📈 Today's progress: {stats['today_questions']}/{stats['total_questions']} questions\n"
            f"🏆 Total quiz score: {stats['total_score']}"
        )
        
        context.user_data.pop('quiz_questions', None)
        context.user_data.pop('quiz_current', None)
        context.user_data.pop('quiz_correct', None)
        context.user_data.pop('quiz_total', None)
        return ConversationHandler.END
    
    question = questions[current]
    options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])])
    
    keyboard = [
        [InlineKeyboardButton(f"{i+1}", callback_data=f"quiz_answer_{i}")]
        for i in range(len(question['options']))
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await update.message.reply_text(
        f"❓ *Question {current+1}/{len(questions)}*\n"
        f"📚 Category: {question['category']}\n\n"
        f"{question['question']}\n\n"
        f"{options_text}\n\n"
        f"⏱️ You have {QUIZ_TIME_LIMIT} seconds to answer.",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Store message ID for editing later
    context.user_data['quiz_message_id'] = message.message_id
    
    # Set a timer for this question
    context.job_queue.run_once(
        quiz_timeout,
        QUIZ_TIME_LIMIT,
        data={
            'user_id': update.effective_user.id,
            'chat_id': update.effective_chat.id,
            'message_id': message.message_id,
            'question_index': current
        },
        name=f"quiz_timeout_{update.effective_user.id}"
    )

async def quiz_timeout(context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz question timeout."""
    job_data = context.job.data
    user_id = job_data['user_id']
    chat_id = job_data['chat_id']
    message_id = job_data['message_id']
    question_index = job_data['question_index']
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="⏰ Time's up! Moving to next question...\n❌ -5 coins",
            reply_markup=None
        )
        
        # Deduct coins for timeout (counts as wrong)
        if deduct_coins(user_id, QUIZ_PENALTY_WRONG, "Quiz timeout penalty"):
            # Move to next question
            # This is tricky because we need the user's context
            # We'll handle this in the callback
            pass
    except Exception as e:
        logger.error(f"Error in quiz timeout: {e}")

@require_user
async def quiz_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show quiz statistics for the user."""
    user_id = update.effective_user.id
    stats = get_quiz_stats(user_id)
    can_play, answered, total = can_play_quiz(user_id)
    
    text = (
        f"📊 *Your Quiz Statistics*\n\n"
        f"🏆 Total Score: {stats['total_score']}\n"
        f"📚 Questions Answered: {stats['total_questions']}\n\n"
        f"📈 *Today's Progress:*\n"
        f"Questions: {stats['today_questions']}/{total}\n"
        f"Earnings: {stats['today_earnings']} coins\n\n"
        f"⏭️ Remaining: {total - answered}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@require_user
async def quiz_leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show quiz leaderboard."""
    top_users = get_quiz_leaderboard(10)
    if not top_users:
        await update.message.reply_text("No quiz participants yet.")
        return
    text = "📚 *Quiz Leaderboard – Top Scorers*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        name = user['first_name'] or f"User{user['user_id']}"
        if user['username']:
            name += f" (@{user['username']})"
        score = user['score']
        text += f"{medal} {escape_markdown(name)} – `{score}` points\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== ADMIN COMMANDS ====================
@admin_only
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
    banned_users = c.fetchone()[0]
    c.execute("SELECT SUM(coins) FROM users")
    total_coins = c.fetchone()[0] or 0
    c.execute("SELECT SUM(quiz_score) FROM users")
    total_quiz_score = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM quiz_history WHERE date(played_at) = date('now')")
    today_quiz = c.fetchone()[0]
    conn.close()
    text = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 Total Users: {total_users}\n"
        f"⛔ Banned Users: {banned_users}\n"
        f"💰 Total Coins: {total_coins}\n"
        f"📚 Total Quiz Score: {total_quiz_score}\n"
        f"🎯 Today's Quiz Attempts: {today_quiz}\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@admin_only
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = c.fetchall()
    conn.close()
    sent = 0
    failed = 0
    for (user_id,) in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 *Broadcast:*\n\n{message}", parse_mode=ParseMode.MARKDOWN)
            sent += 1
        except Exception as e:
            logger.error(f"Broadcast failed to {user_id}: {e}")
            failed += 1
    await update.message.reply_text(f"✅ Broadcast sent.\nSent: {sent}\nFailed: {failed}")

@admin_only
async def admin_addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addcoins <user_id> <amount>")
        return
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid user_id or amount.")
        return
    add_coins(target_id, amount, "Admin add")
    await update.message.reply_text(f"✅ Added {amount} coins to user {target_id}.")

@admin_only
async def admin_removecoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /removecoins <user_id> <amount>")
        return
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid user_id or amount.")
        return
    if deduct_coins(target_id, amount, "Admin remove"):
        await update.message.reply_text(f"✅ Removed {amount} coins from user {target_id}.")
    else:
        await update.message.reply_text("❌ User doesn't have enough coins.")

@admin_only
async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ban <user_id> [hours] [reason]")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user_id.")
        return
    hours = None
    reason = "No reason provided"
    if len(context.args) >= 2:
        try:
            hours = int(context.args[1])
            if len(context.args) >= 3:
                reason = " ".join(context.args[2:])
        except ValueError:
            reason = " ".join(context.args[1:])
    ban_user(target_id, update.effective_user.id, reason, hours)
    await update.message.reply_text(f"✅ User {target_id} banned. Reason: {reason}" + (f" for {hours} hours" if hours else " permanently"))

@admin_only
async def admin_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user_id.")
        return
    unban_user(target_id)
    await update.message.reply_text(f"✅ User {target_id} unbanned.")

@admin_only
async def admin_listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, coins, is_banned, last_active, quiz_score FROM users ORDER BY last_active DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    text = "📋 *Recent Users (last 20):*\n\n"
    for row in rows:
        user_id, username, first_name, coins, banned, last_active, quiz_score = row
        name = escape_markdown(first_name or "No name")
        username_str = f" @{escape_markdown(username)}" if username else ""
        banned_str = "⛔" if banned else "✅"
        user_id_escaped = escape_markdown(str(user_id))
        coins_escaped = escape_markdown(str(coins))
        quiz_escaped = escape_markdown(str(quiz_score))
        text += f"{banned_str} {name}{username_str} (ID: `{user_id_escaped}`) – {coins_escaped} coins | Quiz: {quiz_escaped} – Last: {last_active[:10]}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@admin_only
async def admin_setdaily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /setdaily <min> <max>")
        return
    try:
        min_val = int(context.args[0])
        max_val = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid numbers.")
        return
    if min_val > max_val:
        await update.message.reply_text("Min cannot be greater than max.")
        return
    set_setting("daily_min", str(min_val))
    set_setting("daily_max", str(max_val))
    await update.message.reply_text(f"✅ Daily bonus range set to {min_val}-{max_val} coins.")

@admin_only
async def admin_gencode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        coins = int(context.args[0])
        max_uses = int(context.args[1]) if len(context.args) > 1 else 1
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /gencode <coins> [max_uses=1]")
        return
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO redeem_codes (code, coins, max_uses, created_by) VALUES (?, ?, ?, ?)",
        (code, coins, max_uses, update.effective_user.id),
    )
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"✅ Code generated: `{code}`\nCoins: {coins}\nMax uses: {max_uses}",
        parse_mode=ParseMode.MARKDOWN
    )

@admin_only
async def admin_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = is_maintenance()
    new = "0" if current else "1"
    set_setting("maintenance", new)
    status = "ON" if new == "1" else "OFF"
    await update.message.reply_text(f"🛠️ Maintenance mode is now **{status}**.", parse_mode=ParseMode.MARKDOWN)

@admin_only
async def admin_resetcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset all users' coins to zero."""
    reset_all_coins()
    await update.message.reply_text("✅ All users' coins have been reset to 0.")

@admin_only
async def admin_setrewardtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set daily reward time (UTC). Usage: /setrewardtime <hour> <minute>"""
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /setrewardtime <hour> <minute> (UTC)")
        return
    try:
        hour = int(context.args[0])
        minute = int(context.args[1])
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid time. Hour must be 0-23, minute 0-59.")
        return
    set_setting("reward_hour", str(hour))
    set_setting("reward_minute", str(minute))
    # Reschedule the job
    context.application.job_queue.run_daily(
        daily_reward_job,
        time=time(hour=hour, minute=minute, tzinfo=None),
        name="daily_top_reward"
    )
    await update.message.reply_text(f"✅ Daily reward time set to {hour:02d}:{minute:02d} UTC. Job rescheduled.")

@admin_only
async def admin_rewardstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hour = int(get_setting("reward_hour", "0"))
    minute = int(get_setting("reward_minute", "0"))
    await update.message.reply_text(f"⏰ Daily reward time: {hour:02d}:{minute:02d} UTC")

@admin_only
async def admin_quizsettings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show or set quiz settings."""
    if len(context.args) == 0:
        questions = get_setting("quiz_questions_per_day", "5")
        reward = get_setting("quiz_reward_correct", "5")
        penalty = get_setting("quiz_penalty_wrong", "5")
        await update.message.reply_text(
            f"📊 *Quiz Settings*\n\n"
            f"📚 Questions per day: {questions}\n"
            f"✅ Reward per correct: {reward} coins\n"
            f"❌ Penalty per wrong: {penalty} coins",
            parse_mode=ParseMode.MARKDOWN
        )
    elif len(context.args) == 3:
        try:
            questions = int(context.args[0])
            reward = int(context.args[1])
            penalty = int(context.args[2])
            if questions < 1 or reward < 0 or penalty < 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid values. Use: /quizsettings <questions> <reward> <penalty>")
            return
        set_setting("quiz_questions_per_day", str(questions))
        set_setting("quiz_reward_correct", str(reward))
        set_setting("quiz_penalty_wrong", str(penalty))
        await update.message.reply_text(f"✅ Quiz settings updated!")
    else:
        await update.message.reply_text("Usage: /quizsettings OR /quizsettings <questions> <reward> <penalty>")

# ==================== ADMIN PANEL ====================
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    maint_status = "🔴 ON" if is_maintenance() else "🟢 OFF"
    keyboard = [
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("➕ Add Coins", callback_data="admin_addcoins")],
        [InlineKeyboardButton("➖ Remove Coins", callback_data="admin_removecoins")],
        [InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban")],
        [InlineKeyboardButton("✅ Unban User", callback_data="admin_unban")],
        [InlineKeyboardButton("📋 List Users", callback_data="admin_listusers")],
        [InlineKeyboardButton("🎲 Set Daily Range", callback_data="admin_setdaily")],
        [InlineKeyboardButton("🎟️ Generate Code", callback_data="admin_gencode")],
        [InlineKeyboardButton("💰 Reset All Coins", callback_data="admin_resetcoins")],
        [InlineKeyboardButton("⏰ Set Reward Time", callback_data="admin_setrewardtime")],
        [InlineKeyboardButton("⏱️ Reward Status", callback_data="admin_rewardstatus")],
        [InlineKeyboardButton("📊 Quiz Settings", callback_data="admin_quizsettings")],
        [InlineKeyboardButton(f"🛠️ Maintenance {maint_status}", callback_data="admin_maintenance")],
        [InlineKeyboardButton("🔙 Close", callback_data="admin_close")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🛠️ *Admin Panel* – choose an action:", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

# ==================== MENU HANDLERS (Inline Keyboards) ====================
async def guild_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Guild Info", callback_data="guild_info")],
        [InlineKeyboardButton("➕ Join Guild (20 coins)", callback_data="guild_join")],
        [InlineKeyboardButton("➖ Leave Guild (10 coins)", callback_data="guild_leave")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🛡️ *Guild Management*\nSelect an option:",
        reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
    )

async def friend_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 List Friends", callback_data="friend_list")],
        [InlineKeyboardButton("❌ Remove Friend (15 coins)", callback_data="friend_remove")],
        [InlineKeyboardButton("📨 Pending Requests", callback_data="friend_pending")],
        [InlineKeyboardButton("✅ Accept Request (5 coins)", callback_data="friend_accept")],
        [InlineKeyboardButton("❎ Reject Request", callback_data="friend_reject")],
        [InlineKeyboardButton("➕ Send Friend Request (5 coins)", callback_data="friend_send")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👥 *Friend Management*\nSelect an option:",
        reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
    )

async def long_bio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 By UID/Password (20 coins)", callback_data="bio_uid")],
        [InlineKeyboardButton("🔑 By Access Token (15 coins)", callback_data="bio_access")],
        [InlineKeyboardButton("🔗 Get EAT Token", callback_data="get_eat_link")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📝 *Long Bio Update*\nChoose method:",
        reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
    )

async def token_tools_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔑 Generate JWT (UID/Pass)", callback_data="jwt_gen")],
        [InlineKeyboardButton("🔄 Access Token → JWT", callback_data="access_to_jwt")],
        [InlineKeyboardButton("🔄 EAT → Access Token", callback_data="eat_to_access")],
        [InlineKeyboardButton("🔄 EAT → JWT", callback_data="eat_to_jwt")],
        [InlineKeyboardButton("🔗 Get EAT Token Link", callback_data="get_eat_link")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔧 *Token Tools*\nSelect an option:",
        reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
    )

# ==================== GUEST GENERATOR CONVERSATION ====================
async def guest_generator_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌍 Please enter the region (e.g., IND, BD, SG):")
    return REGION

async def guest_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["guest_region"] = update.message.text.upper()
    await update.message.reply_text("📝 Please enter a name (any text):")
    return NAME

async def guest_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["guest_name"] = update.message.text
    await update.message.reply_text("🔢 How many accounts do you want? (Minimum 15, cost: 5 coins per account)")
    return COUNT

async def guest_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text)
        if count < 15:
            await update.message.reply_text("❌ Minimum 15 accounts required. Please enter a number >= 15.")
            return COUNT
        if count > 50:
            await update.message.reply_text("❌ Maximum 50 accounts allowed at once. Please enter a number <= 50.")
            return COUNT
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Please enter a number.")
        return COUNT

    user_id = update.effective_user.id
    total_cost = count * COST_GUEST_PER_ACCOUNT
    if not deduct_coins(user_id, total_cost, f"Guest generation for {count} accounts"):
        await update.message.reply_text(f"❌ Insufficient coins! You need {total_cost} coins.")
        return ConversationHandler.END

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    processing_msg = await update.message.reply_text("⏳ Generating accounts, please wait...")

    region = context.user_data["guest_region"]
    name = context.user_data["guest_name"]
    success, result = generate_guest(name, count, region)

    if success:
        data = result
        accounts = data.get("accounts", [])
        if accounts:
            filename = f"guest_accounts_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_content = ""
            for acc in accounts:
                line = f"UID: {acc['uid']} | Password: {acc['password']} | Region: {acc['region']}\n"
                file_content += line
            with open(filename, 'w') as f:
                f.write(file_content)
            await processing_msg.delete()
            with open(filename, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=f"✅ Generated {len(accounts)} accounts (cost {total_cost} coins)"
                )
            os.remove(filename)
        else:
            await processing_msg.edit_text("⚠️ Generation succeeded but no accounts returned.")
            add_coins(user_id, total_cost, "Refund for failed guest generation")
    else:
        await processing_msg.edit_text(f"❌ Generation failed: {result}")
        add_coins(user_id, total_cost, "Refund for failed guest generation")

    context.user_data.pop("guest_region", None)
    context.user_data.pop("guest_name", None)
    return ConversationHandler.END

async def guest_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Guest generation cancelled.")
    return ConversationHandler.END

# ==================== FRIEND MANAGEMENT CONVERSATION ====================
async def friend_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    cost = 0
    if data == "friend_remove":
        cost = 15
    elif data == "friend_accept":
        cost = 5
    elif data == "friend_send":
        cost = COST_SEND_FRIEND_REQUEST

    if cost > 0 and not deduct_coins(user_id, cost, f"Friend action: {data}"):
        await query.edit_message_text(f"❌ Insufficient coins! You need {cost} coins.")
        return ConversationHandler.END

    context.user_data["friend_action"] = data
    context.user_data["friend_cost"] = cost

    if data in ["friend_list", "friend_pending"]:
        await query.edit_message_text("👤 Please enter your UID:")
        return FRIEND_UID
    else:
        if data == "friend_remove":
            prompt = "❌ Please enter the UID of the friend you want to remove:"
        elif data == "friend_accept":
            prompt = "✅ Please enter the UID of the requester you want to accept:"
        elif data == "friend_reject":
            prompt = "❎ Please enter the UID of the requester you want to reject:"
        elif data == "friend_send":
            prompt = "➕ Please enter the UID of the person you want to send a friend request to:"
        await query.edit_message_text(prompt)
        return FRIEND_TARGET

async def friend_get_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["friend_target"] = update.message.text.strip()
    await update.message.reply_text("👤 Now enter your UID:")
    return FRIEND_UID

async def friend_get_uid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["friend_uid"] = update.message.text.strip()
    await update.message.reply_text("🔑 Now enter your password:")
    return FRIEND_PASSWORD

async def friend_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    uid = context.user_data["friend_uid"]
    action = context.user_data["friend_action"]
    cost = context.user_data.get("friend_cost", 0)
    target = context.user_data.get("friend_target")

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    processing = await update.message.reply_text("⏳ Processing, please wait...")

    success = False
    result = None
    endpoint = ""
    params = {}

    if action == "friend_list":
        endpoint = "get_friends_list"
        params = {"uid": uid, "password": password}
    elif action == "friend_remove":
        endpoint = "remove_friend"
        params = {"uid": uid, "password": password, "friend_uid": target}
    elif action == "friend_pending":
        endpoint = "get_pending_requests"
        params = {"uid": uid, "password": password}
    elif action == "friend_accept":
        endpoint = "accept_friend_request"
        params = {"uid": uid, "password": password, "friend_uid": target}
    elif action == "friend_reject":
        endpoint = "reject_friend_request"
        params = {"uid": uid, "password": password, "friend_uid": target}
    elif action == "friend_send":
        endpoint = "send_friend_request"
        params = {"uid": uid, "password": password, "target_uid": target}
        # If endpoint doesn't exist yet, it will fail gracefully

    if endpoint:
        success, result = call_friend_api(endpoint, params)

    await processing.delete()
    if success:
        if action in ["friend_list", "friend_pending"]:
            items = result if isinstance(result, list) else result.get("friends" if action=="friend_list" else "requests", [])
            if items:
                msg = f"👥 *{'Friends' if action=='friend_list' else 'Pending Requests'}:*\n"
                for item in items[:10]:
                    name = escape_markdown(str(item.get('name', 'Unknown')))
                    item_uid = escape_markdown(str(item.get('uid', '')))
                    msg += f"\n• {name} (UID: `{item_uid}`)"
                await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("No items found.")
        else:
            await update.message.reply_text(f"✅ Action completed successfully!")
    else:
        await update.message.reply_text(f"❌ Failed: {result}")
        if cost > 0:
            add_coins(update.effective_user.id, cost, f"Refund for failed {action}")

    context.user_data.clear()
    return ConversationHandler.END

async def friend_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cost = context.user_data.get("friend_cost", 0)
    if cost > 0:
        add_coins(user_id, cost, "Refund for cancelled friend action")
    await update.message.reply_text("Friend action cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# ==================== QUIZ CALLBACK HANDLER ====================
async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if not data.startswith("quiz_answer_"):
        return
    
    user_id = query.from_user.id
    answer_index = int(data.split("_")[2])
    
    # Check if this user has an active quiz
    if 'quiz_questions' not in context.user_data:
        await query.edit_message_text("❌ Quiz session expired. Please start a new quiz with /quiz.")
        return
    
    current = context.user_data['quiz_current']
    questions = context.user_data['quiz_questions']
    
    if current >= len(questions):
        await query.edit_message_text("❌ Quiz already completed.")
        return
    
    question = questions[current]
    correct = (answer_index == question['correct'])
    
    # Cancel the timeout job
    current_jobs = context.job_queue.get_jobs_by_name(f"quiz_timeout_{user_id}")
    for job in current_jobs:
        job.schedule_removal()
    
    if correct:
        coins_earned = QUIZ_REWARD_CORRECT
        add_coins(user_id, coins_earned, f"Quiz correct: Q{current+1}")
        context.user_data['quiz_correct'] += 1
        result_text = f"✅ Correct! +{coins_earned} coins"
    else:
        coins_earned = -QUIZ_PENALTY_WRONG
        deduct_coins(user_id, QUIZ_PENALTY_WRONG, f"Quiz wrong: Q{current+1}")
        result_text = f"❌ Wrong! -{QUIZ_PENALTY_WRONG} coins\nCorrect answer: {question['correct']+1}. {question['options'][question['correct']]}"
    
    # Record the answer
    record_quiz_answer(user_id, question, answer_index, correct, coins_earned if correct else -QUIZ_PENALTY_WRONG)
    
    # Update the message
    await query.edit_message_text(
        f"{result_text}\n\n"
        f"📊 Progress: {context.user_data['quiz_correct']}/{current+1} correct"
    )
    
    # Move to next question
    context.user_data['quiz_current'] += 1
    
    # Send next question
    await send_quiz_question(update, context)

# ==================== CALLBACK QUERY HANDLERS (non-conversation) ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if is_maintenance() and user_id not in ADMIN_IDS:
        await query.edit_message_text(MAINTENANCE_MESSAGE, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "back_to_main":
        await query.edit_message_text("Returning to main menu...")
        return

    # Admin panel actions
    if data.startswith("admin_"):
        if user_id not in ADMIN_IDS:
            await query.edit_message_text("⛔ Unauthorized.")
            return
        if data == "admin_stats":
            await admin_stats(update, context)
            await query.message.delete()
        elif data == "admin_broadcast":
            await query.edit_message_text("📢 Send the message you want to broadcast:")
            context.user_data["admin_action"] = "broadcast"
        elif data == "admin_addcoins":
            await query.edit_message_text("➕ Send: `user_id amount`")
            context.user_data["admin_action"] = "addcoins"
        elif data == "admin_removecoins":
            await query.edit_message_text("➖ Send: `user_id amount`")
            context.user_data["admin_action"] = "removecoins"
        elif data == "admin_ban":
            await query.edit_message_text("🚫 Send: `user_id [hours] [reason]`\nExample: `123456789 24 spamming`")
            context.user_data["admin_action"] = "ban"
        elif data == "admin_unban":
            await query.edit_message_text("✅ Send the user ID to unban:")
            context.user_data["admin_action"] = "unban"
        elif data == "admin_listusers":
            await admin_listusers(update, context)
            await query.message.delete()
        elif data == "admin_setdaily":
            await query.edit_message_text("🎲 Send: `min max` (e.g., `10 50`)")
            context.user_data["admin_action"] = "setdaily"
        elif data == "admin_gencode":
            await query.edit_message_text("🎟️ Send: `coins [max_uses]` (e.g., `100 5`)")
            context.user_data["admin_action"] = "gencode"
        elif data == "admin_resetcoins":
            reset_all_coins()
            await query.edit_message_text("✅ All users' coins have been reset to 0.")
        elif data == "admin_setrewardtime":
            await query.edit_message_text("⏰ Send the reward time in format: `hour minute` (UTC, e.g., `0 0` for midnight)")
            context.user_data["admin_action"] = "setrewardtime"
        elif data == "admin_rewardstatus":
            hour = int(get_setting("reward_hour", "0"))
            minute = int(get_setting("reward_minute", "0"))
            await query.edit_message_text(f"⏰ Daily reward time: {hour:02d}:{minute:02d} UTC")
        elif data == "admin_quizsettings":
            questions = get_setting("quiz_questions_per_day", "5")
            reward = get_setting("quiz_reward_correct", "5")
            penalty = get_setting("quiz_penalty_wrong", "5")
            await query.edit_message_text(
                f"📊 *Quiz Settings*\n\n"
                f"📚 Questions per day: {questions}\n"
                f"✅ Reward per correct: {reward} coins\n"
                f"❌ Penalty per wrong: {penalty} coins\n\n"
                f"To change, use: /quizsettings <questions> <reward> <penalty>",
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == "admin_maintenance":
            current = is_maintenance()
            new = "0" if current else "1"
            set_setting("maintenance", new)
            status = "ON" if new == "1" else "OFF"
            await query.edit_message_text(f"🛠️ Maintenance mode is now **{status}**.", parse_mode=ParseMode.MARKDOWN)
        elif data == "admin_close":
            await query.message.delete()
        return

    # Guild actions (direct, not conversation)
    if data == "guild_info":
        await query.edit_message_text("📊 Send the Guild ID:")
        context.user_data["action"] = "guild_info"
    elif data == "guild_join":
        if not deduct_coins(user_id, 20, "Guild join attempt"):
            await query.edit_message_text("❌ Insufficient coins! You need 20 coins.")
            return
        await query.edit_message_text("➕ Send the Guild ID you want to join:")
        context.user_data["action"] = "guild_join"
    elif data == "guild_leave":
        if not deduct_coins(user_id, 10, "Guild leave attempt"):
            await query.edit_message_text("❌ Insufficient coins! You need 10 coins.")
            return
        await query.edit_message_text("➖ Send the Guild ID you want to leave:")
        context.user_data["action"] = "guild_leave"
    elif data == "bio_uid":
        if not deduct_coins(user_id, 20, "Bio update via UID"):
            await query.edit_message_text("❌ Insufficient coins! You need 20 coins.")
            return
        await query.edit_message_text("📝 Send: `UID PASSWORD BIO`")
        context.user_data["action"] = "bio_uid"
    elif data == "bio_access":
        if not deduct_coins(user_id, 15, "Bio update via Access Token"):
            await query.edit_message_text("❌ Insufficient coins! You need 15 coins.")
            return
        await query.edit_message_text("🔑 Send: `ACCESS_TOKEN BIO`")
        context.user_data["action"] = "bio_access"
    elif data == "jwt_gen":
        if not deduct_coins(user_id, COST_JWT_GEN, "JWT generation"):
            await query.edit_message_text(f"❌ Insufficient coins! You need {COST_JWT_GEN} coins.")
            return
        await query.edit_message_text("🔑 Send your UID and Password in format: `UID PASSWORD`")
        context.user_data["action"] = "jwt_gen"
    elif data == "access_to_jwt":
        if not deduct_coins(user_id, COST_ACCESS_TO_JWT, "Access Token to JWT"):
            await query.edit_message_text(f"❌ Insufficient coins! You need {COST_ACCESS_TO_JWT} coins.")
            return
        await query.edit_message_text("🔄 Send your Access Token:")
        context.user_data["action"] = "access_to_jwt"
    elif data == "eat_to_access":
        if not deduct_coins(user_id, COST_EAT_TO_ACCESS, "EAT to Access Token"):
            await query.edit_message_text(f"❌ Insufficient coins! You need {COST_EAT_TO_ACCESS} coins.")
            return
        await query.edit_message_text("🔄 Send your EAT Token:")
        context.user_data["action"] = "eat_to_access"
    elif data == "eat_to_jwt":
        if not deduct_coins(user_id, COST_EAT_TO_JWT, "EAT to JWT"):
            await query.edit_message_text(f"❌ Insufficient coins! You need {COST_EAT_TO_JWT} coins.")
            return
        await query.edit_message_text("🔄 Send your EAT Token:")
        context.user_data["action"] = "eat_to_jwt"
    elif data == "get_eat_link":
        await query.edit_message_text("🔗 Click here to get your EAT Token: https://t.me/sulav_bio/5")
    else:
        await query.edit_message_text("Unknown option.")

# ==================== MESSAGE HANDLERS (Non-conversation) ====================
@require_user
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    action = context.user_data.get("action")
    admin_action = context.user_data.get("admin_action")

    # Handle admin input first
    if admin_action:
        if user_id not in ADMIN_IDS:
            context.user_data.pop("admin_action", None)
            return
        if admin_action == "broadcast":
            context.args = text.split()
            await admin_broadcast(update, context)
        elif admin_action == "addcoins":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: `user_id amount`")
                return
            context.args = parts
            await admin_addcoins(update, context)
        elif admin_action == "removecoins":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: `user_id amount`")
                return
            context.args = parts
            await admin_removecoins(update, context)
        elif admin_action == "ban":
            parts = text.split()
            if len(parts) < 1:
                await update.message.reply_text("❌ Invalid format. Use: `user_id [hours] [reason]`")
                return
            context.args = parts
            await admin_ban(update, context)
        elif admin_action == "unban":
            context.args = [text]
            await admin_unban(update, context)
        elif admin_action == "setdaily":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: `min max`")
                return
            context.args = parts
            await admin_setdaily(update, context)
        elif admin_action == "gencode":
            parts = text.split()
            if len(parts) < 1:
                await update.message.reply_text("❌ Invalid format. Use: `coins [max_uses]`")
                return
            context.args = parts
            await admin_gencode(update, context)
        elif admin_action == "setrewardtime":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: `hour minute` (UTC)")
                return
            try:
                hour = int(parts[0])
                minute = int(parts[1])
                if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                    raise ValueError
            except ValueError:
                await update.message.reply_text("Invalid time. Hour must be 0-23, minute 0-59.")
                return
            set_setting("reward_hour", str(hour))
            set_setting("reward_minute", str(minute))
            # Reschedule job
            context.application.job_queue.run_daily(
                daily_reward_job,
                time=time(hour=hour, minute=minute, tzinfo=None),
                name="daily_top_reward"
            )
            await update.message.reply_text(f"✅ Daily reward time set to {hour:02d}:{minute:02d} UTC.")
        context.user_data.pop("admin_action", None)
        return

    # Main menu navigation (no active action)
    if not action:
        if text == "🛡️ Guild":
            await guild_menu(update, context)
        elif text == "👥 Friend":
            await friend_menu(update, context)
        elif text == "📝 Long Bio":
            await long_bio_menu(update, context)
        elif text == "🎫 Guest Gen":
            # Handled by conversation handler
            pass
        elif text == "🔧 Token Tools":
            await token_tools_menu(update, context)
        elif text == "ℹ️ Player Info":
            await update.message.reply_text("🔍 Send the player UID and region in format: `UID REGION`\n(e.g., `123456789 IND`)")
            context.user_data["action"] = "player_info"
        elif text == "🚫 Ban Check":
            await update.message.reply_text("🚫 Send the player UID:")
            context.user_data["action"] = "ban_check"
        elif text == "🎉 Event Info":
            await update.message.reply_text("🎉 Send the region (e.g., IND, BD, SG):")
            context.user_data["action"] = "event_info"
        elif text == "📦 Jwt Gen":
            if not deduct_coins(user_id, COST_JWT_GEN, "JWT generation"):
                await update.message.reply_text(f"❌ Insufficient coins! You need {COST_JWT_GEN} coins.")
                return
            await update.message.reply_text("🔑 Send your UID and Password in format: `UID PASSWORD`")
            context.user_data["action"] = "jwt_gen"
        elif text == "👤 Wallet":
            await wallet_command(update, context)
        elif text == "💰 Daily":
            await daily_bonus(update, context)
        elif text == "🎁 Refer":
            await refer_command(update, context)
        elif text == "🏆 Redeem":
            await update.message.reply_text("Send your redeem code (or use /redeem <code>):")
            context.user_data["action"] = "redeem"
        elif text == "🏅 Leaderboard":
            await leaderboard_command(update, context)
        elif text == "📊 Quiz":
            await quiz_command(update, context)
        elif text == "📈 Quiz Stats":
            await quiz_stats_command(update, context)
        else:
            await update.message.reply_text("Please use the menu buttons.")
        return

    # Process active actions (non-conversation ones)
    if action == "redeem":
        code = text.upper()
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT coins, max_uses, used_count FROM redeem_codes WHERE code = ? AND (expires_at IS NULL OR expires_at > datetime('now'))",
            (code,)
        )
        row = c.fetchone()
        if not row:
            await update.message.reply_text("❌ Invalid or expired code.")
        else:
            coins, max_uses, used_count = row
            if used_count >= max_uses:
                await update.message.reply_text("❌ This code has reached its maximum uses.")
            else:
                c.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
                conn.commit()
                add_coins(user_id, coins, f"Redeemed code {code}")
                await update.message.reply_text(f"✅ Success! You received {coins} coins.")
        conn.close()
        context.user_data.pop("action", None)

    # Guild actions
    elif action == "guild_info":
        guild_id = text
        await update.message.reply_text("Now send the region (e.g., IND, SG, BD):")
        context.user_data["guild_id"] = guild_id
        context.user_data["action"] = "guild_info_region"
    elif action == "guild_info_region":
        region = text.upper()
        guild_id = context.user_data.get("guild_id")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Fetching guild info...")
        success, result = call_guild_api("guild", {"guild_id": guild_id, "region": region})
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename=f"guild_{guild_id}.json",
                caption=f"✅ Guild info for {guild_id} ({region})"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
        context.user_data.pop("action", None)
        context.user_data.pop("guild_id", None)
    elif action == "guild_join":
        guild_id = text
        await update.message.reply_text("Now send your UID and Password in format: `UID PASSWORD`", parse_mode=ParseMode.MARKDOWN)
        context.user_data["guild_id"] = guild_id
        context.user_data["action"] = "guild_join_creds"
    elif action == "guild_join_creds":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: UID PASSWORD")
            return
        uid, password = parts
        guild_id = context.user_data.get("guild_id")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Joining guild...")
        success, result = call_guild_api("join", {"guild_id": guild_id, "uid": uid, "password": password})
        await processing.delete()
        if success:
            await update.message.reply_text(f"✅ Joined guild successfully!")
        else:
            await update.message.reply_text(f"❌ Failed to join: {result}")
            add_coins(user_id, 20, "Refund for failed guild join")
        context.user_data.pop("action", None)
        context.user_data.pop("guild_id", None)
    elif action == "guild_leave":
        guild_id = text
        await update.message.reply_text("Now send your UID and Password in format: `UID PASSWORD`", parse_mode=ParseMode.MARKDOWN)
        context.user_data["guild_id"] = guild_id
        context.user_data["action"] = "guild_leave_creds"
    elif action == "guild_leave_creds":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: UID PASSWORD")
            return
        uid, password = parts
        guild_id = context.user_data.get("guild_id")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Leaving guild...")
        success, result = call_guild_api("leave", {"guild_id": guild_id, "uid": uid, "password": password})
        await processing.delete()
        if success:
            await update.message.reply_text(f"✅ Left guild successfully!")
        else:
            await update.message.reply_text(f"❌ Failed to leave: {result}")
            add_coins(user_id, 10, "Refund for failed guild leave")
        context.user_data.pop("action", None)
        context.user_data.pop("guild_id", None)

    # Bio actions
    elif action == "bio_uid":
        parts = text.split(maxsplit=2)
        if len(parts) != 3:
            await update.message.reply_text("❌ Invalid format. Use: UID PASSWORD BIO")
            return
        uid, password, bio = parts
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Updating bio...")
        success, msg = update_long_bio(uid=uid, password=password, bio=bio)
        await processing.delete()
        if success:
            await update.message.reply_text(f"✅ Bio updated successfully!")
        else:
            await update.message.reply_text(f"❌ Failed: {msg}")
            add_coins(user_id, 20, "Refund for failed bio update")
        context.user_data.pop("action", None)
    elif action == "bio_access":
        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: ACCESS_TOKEN BIO")
            return
        access_token, bio = parts
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Updating bio...")
        success, msg = update_long_bio(access_token=access_token, bio=bio)
        await processing.delete()
        if success:
            await update.message.reply_text(f"✅ Bio updated successfully!")
        else:
            await update.message.reply_text(f"❌ Failed: {msg}")
            add_coins(user_id, 15, "Refund for failed bio update")
        context.user_data.pop("action", None)

    # Other features
    elif action == "player_info":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: `UID REGION`\n(e.g., `123456789 IND`)")
            return
        uid, region = parts[0], parts[1].upper()
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Fetching player info...")
        success, result = get_player_info(uid, region)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename=f"player_{uid}.json",
                caption=f"ℹ️ Player info for UID {uid} ({region})"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_PLAYER_INFO, "Refund for failed player info")
        context.user_data.pop("action", None)

    elif action == "ban_check":
        uid = text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Checking ban status...")
        success, result = check_ban(uid)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename=f"ban_{uid}.json",
                caption=f"🚫 Ban status for UID {uid}"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_BAN_CHECK, "Refund for failed ban check")
        context.user_data.pop("action", None)

    elif action == "event_info":
        region = text.upper()
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Fetching event info...")
        
        try:
            success, result = get_event_info(region)
            await processing.delete()
            
            if success:
                image_sent = False
                if isinstance(result, dict):
                    for key in ['image', 'url', 'link', 'photo', 'banner', 'img']:
                        if key in result and isinstance(result[key], str) and result[key].startswith(('http://', 'https://')):
                            try:
                                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=result[key])
                                image_sent = True
                                break
                            except Exception as e:
                                logger.error(f"Failed to send event image: {e}")
                                continue
                    if not image_sent:
                        json_str = json.dumps(result, indent=2, ensure_ascii=False)
                        await send_long_text(
                            update,
                            json_str,
                            filename=f"event_{region}.json",
                            caption=f"🎉 Event info for {region}"
                        )
                elif isinstance(result, str):
                    if result.startswith(('http://', 'https://')):
                        try:
                            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=result)
                            image_sent = True
                        except:
                            pass
                    if not image_sent:
                        await send_long_text(
                            update,
                            result,
                            filename=f"event_{region}.txt",
                            caption=f"🎉 Event info for {region}"
                        )
                else:
                    await update.message.reply_text(f"🎉 Event info:\n{result}")
            else:
                await update.message.reply_text(f"❌ Failed: {result}")
                add_coins(user_id, COST_EVENT_INFO, "Refund for failed event info")
        except Exception as e:
            logger.error(f"🔥 CRITICAL ERROR in event_info: {str(e)}", exc_info=True)
            await processing.delete()
            await update.message.reply_text(
                f"❌ An error occurred while fetching event info.\n"
                f"Error details: {str(e)[:200]}"
            )
            add_coins(user_id, COST_EVENT_INFO, "Refund for event info error")
        
        context.user_data.pop("action", None)

    elif action == "jwt_gen":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ Invalid format. Use: UID PASSWORD")
            return
        uid, password = parts
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Generating JWT token...")
        success, result = generate_jwt(uid, password)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename=f"jwt_{uid}.json",
                caption=f"🔑 JWT Token for UID {uid}"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_JWT_GEN, "Refund for failed JWT generation")
        context.user_data.pop("action", None)

    elif action == "access_to_jwt":
        access_token = text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Converting Access Token to JWT...")
        success, result = access_to_jwt(access_token)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename="jwt_from_access.json",
                caption="🔄 JWT from Access Token"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_ACCESS_TO_JWT, "Refund for failed conversion")
        context.user_data.pop("action", None)

    elif action == "eat_to_access":
        eat_token = text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Converting EAT to Access Token...")
        success, result = eat_to_access(eat_token)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename="access_from_eat.json",
                caption="🔄 Access Token from EAT"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_EAT_TO_ACCESS, "Refund for failed conversion")
        context.user_data.pop("action", None)

    elif action == "eat_to_jwt":
        eat_token = text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        processing = await update.message.reply_text("⏳ Converting EAT to JWT...")
        success, result = eat_to_jwt(eat_token)
        await processing.delete()
        if success:
            await send_long_text(
                update,
                json.dumps(result, indent=2),
                filename="jwt_from_eat.json",
                caption="🔄 JWT from EAT"
            )
        else:
            await update.message.reply_text(f"❌ Failed: {result}")
            add_coins(user_id, COST_EAT_TO_JWT, "Refund for failed conversion")
        context.user_data.pop("action", None)

    else:
        await update.message.reply_text("Unknown action. Please start over using the menu.")

# ==================== DAILY REWARD JOB ====================
async def daily_reward_job(context: ContextTypes.DEFAULT_TYPE):
    """Job to give daily rewards to top users."""
    top_users = give_daily_top_rewards()
    if top_users:
        logger.info(f"Daily rewards given to top {len(top_users)} users: {[u['user_id'] for u in top_users]}")

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    print("🔥 EXCEPTION:", context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An internal error occurred. The developers have been notified. Please try again later."
        )

# ==================== MAIN ====================
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Set up daily reward job
    hour = int(get_setting("reward_hour", "0"))
    minute = int(get_setting("reward_minute", "0"))
    app.job_queue.run_daily(
        daily_reward_job,
        time=time(hour=hour, minute=minute, tzinfo=None),
        name="daily_top_reward"
    )

    # Conversation handler for guest generator
    guest_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🎫 Guest Gen$'), guest_generator_start)],
        states={
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, guest_region)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, guest_name)],
            COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, guest_count)],
        },
        fallbacks=[CommandHandler("cancel", guest_cancel)],
    )

    # Conversation handler for friend management
    friend_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(friend_start, pattern="^friend_(list|remove|pending|accept|reject|send)$")
        ],
        states={
            FRIEND_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_get_target)],
            FRIEND_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_get_uid)],
            FRIEND_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, friend_execute)],
        },
        fallbacks=[CommandHandler("cancel", friend_cancel)],
    )

    # Quiz conversation handler
    quiz_conv = ConversationHandler(
        entry_points=[
            CommandHandler("quiz", quiz_command),
            MessageHandler(filters.Regex('^📊 Quiz$'), quiz_command)
        ],
        states={
            QUIZ_ACTIVE: [CallbackQueryHandler(quiz_callback, pattern="^quiz_answer_")]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
    )

    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("wallet", wallet_command))
    app.add_handler(CommandHandler("daily", daily_bonus))
    app.add_handler(CommandHandler("refer", refer_command))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("setuid", setuid_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("quizstats", quiz_stats_command))
    app.add_handler(CommandHandler("quizlb", quiz_leaderboard_command))

    # Admin commands
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    app.add_handler(CommandHandler("addcoins", admin_addcoins))
    app.add_handler(CommandHandler("removecoins", admin_removecoins))
    app.add_handler(CommandHandler("ban", admin_ban))
    app.add_handler(CommandHandler("unban", admin_unban))
    app.add_handler(CommandHandler("listusers", admin_listusers))
    app.add_handler(CommandHandler("setdaily", admin_setdaily))
    app.add_handler(CommandHandler("gencode", admin_gencode))
    app.add_handler(CommandHandler("maintenance", admin_maintenance))
    app.add_handler(CommandHandler("resetcoins", admin_resetcoins))
    app.add_handler(CommandHandler("setrewardtime", admin_setrewardtime))
    app.add_handler(CommandHandler("rewardstatus", admin_rewardstatus))
    app.add_handler(CommandHandler("quizsettings", admin_quizsettings))
    app.add_handler(CommandHandler("admin", admin_panel))

    # Callback handler (non-conversation)
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(?!friend_|quiz_)"))

    # Conversation handlers
    app.add_handler(guest_conv)
    app.add_handler(friend_conv)
    app.add_handler(quiz_conv)

    # General message handler (catch-all for non-conversation messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)