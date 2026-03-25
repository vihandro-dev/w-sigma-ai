"""User authentication — signup, login, stored in JSON."""

import json
import os
import hashlib
import secrets

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.json")


def _load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_db(db):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _hash_pw(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, hashed


def signup(username, password):
    username = username.strip().lower()
    if not username or not password:
        return False, "need both username and password"
    if len(username) < 2:
        return False, "username too short"
    if len(password) < 4:
        return False, "password too short (min 4)"

    db = _load_db()
    if username in db:
        return False, "that name is taken fam"

    salt, hashed = _hash_pw(password)
    db[username] = {"password_hash": hashed, "salt": salt}
    _save_db(db)
    return True, "welcome to the squad"


def login(username, password):
    username = username.strip().lower()
    db = _load_db()
    if username not in db:
        return False, "who? dont know that name"

    user = db[username]
    salt, hashed = _hash_pw(password, user["salt"])
    if hashed != user["password_hash"]:
        return False, "wrong password bruh"

    return True, "welcome back"
