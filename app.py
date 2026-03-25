#!/usr/bin/env python3
"""Web app for W_Sigma.ai with login/signup, chat threads, and saved history."""

import os
from flask import Flask, render_template, request, jsonify, session
from chat import send_message, list_chats, load_chat, create_chat, delete_chat
from auth import signup, login
from profiles import load_profile
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", secrets.token_hex(16))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def do_signup():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    ok, msg = signup(username, password)
    if ok:
        session["user"] = username
    return jsonify({"ok": ok, "msg": msg})


@app.route("/login", methods=["POST"])
def do_login():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    ok, msg = login(username, password)
    if ok:
        session["user"] = username
    return jsonify({"ok": ok, "msg": msg})


@app.route("/logout", methods=["POST"])
def do_logout():
    session.pop("user", None)
    return jsonify({"ok": True})


@app.route("/me", methods=["GET"])
def me():
    user = session.get("user")
    if not user:
        return jsonify({"error": "not logged in"}), 401
    profile = load_profile(user)
    return jsonify({
        "username": user,
        "interests": profile.get("interests", []),
        "chat_count": profile.get("chat_count", 0),
    })


@app.route("/chats", methods=["GET"])
def get_chats():
    user = session.get("user")
    if not user:
        return jsonify({"chats": []})
    return jsonify({"chats": list_chats(user)})


@app.route("/chats/new", methods=["POST"])
def new_chat():
    user = session.get("user")
    if not user:
        return jsonify({"error": "not logged in"}), 401
    chat_data = create_chat(user)
    return jsonify(chat_data)


@app.route("/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "not logged in"}), 401
    data = load_chat(user, chat_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)


@app.route("/chats/<chat_id>", methods=["DELETE"])
def del_chat(chat_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "not logged in"}), 401
    delete_chat(user, chat_id)
    return jsonify({"ok": True})


@app.route("/chat", methods=["POST"])
def chat():
    user = session.get("user")
    if not user:
        return jsonify({"error": "not logged in"}), 401

    data = request.get_json()
    message = data.get("message", "").strip()
    chat_id = data.get("chat_id", "")

    if not message:
        return jsonify({"error": "no message"}), 400
    if not chat_id:
        return jsonify({"error": "no chat_id"}), 400

    try:
        reply = send_message(user, chat_id, message)
        return jsonify({"reply": reply})
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            return jsonify({
                "error": "rate_limit",
                "msg": "chill for a sec, too many messages rn. try again in like 30 seconds"
            }), 429
        return jsonify({
            "error": "server_error",
            "msg": "something went wrong on the AI side, try sending that again"
        }), 500


if __name__ == "__main__":
    print("\n  W_Sigma.ai running at http://localhost:8080\n")
    app.run(debug=True, port=8080)
