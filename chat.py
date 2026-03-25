"""Core chat logic with Gemini API + multi-thread chat history + retry logic."""

import json
import os
import re
import time
import uuid
from datetime import datetime
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, SYSTEM_PROMPT
from profiles import load_profile, save_profile, profile_to_text, update_profile_from_chat

client = genai.Client(api_key=GEMINI_API_KEY)

CHATS_DIR = os.path.join(os.path.dirname(__file__), "data", "chats")

# Models in order of preference (best free quota first)
MODELS = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]


def _user_dir(username):
    safe = "".join(c for c in username if c.isalnum() or c in "-_").lower()
    path = os.path.join(CHATS_DIR, safe)
    os.makedirs(path, exist_ok=True)
    return path


def create_chat(username):
    chat_id = uuid.uuid4().hex[:10]
    chat_data = {
        "id": chat_id,
        "title": "new chat",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": [],
    }
    path = os.path.join(_user_dir(username), f"{chat_id}.json")
    with open(path, "w") as f:
        json.dump(chat_data, f, indent=2)
    return chat_data


def list_chats(username):
    user_dir = _user_dir(username)
    chats = []
    for fname in os.listdir(user_dir):
        if fname.endswith(".json"):
            with open(os.path.join(user_dir, fname), "r") as f:
                data = json.load(f)
                chats.append({
                    "id": data["id"],
                    "title": data.get("title", "new chat"),
                    "created": data.get("created", ""),
                    "msg_count": len(data.get("messages", [])),
                })
    chats.sort(key=lambda x: x["created"], reverse=True)
    return chats


def load_chat(username, chat_id):
    path = os.path.join(_user_dir(username), f"{chat_id}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def delete_chat(username, chat_id):
    path = os.path.join(_user_dir(username), f"{chat_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def _save_chat(username, chat_data):
    path = os.path.join(_user_dir(username), f"{chat_data['id']}.json")
    with open(path, "w") as f:
        json.dump(chat_data, f, indent=2)


def _extract_retry_delay(error_msg):
    """Extract retry delay from API error message."""
    match = re.search(r'retryDelay.*?(\d+)', str(error_msg))
    if match:
        return int(match.group(1))
    return 10


def _call_gemini(contents, system_instruction):
    """Call Gemini with retry logic and model fallback."""
    last_error = None

    for model_name in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                    ),
                )
                if response.text:
                    return response.text
            except Exception as e:
                last_error = e
                error_str = str(e)

                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if "limit: 0" in error_str:
                        # This model is completely blocked, skip to next
                        break

                    # Rate limited — wait and retry
                    delay = _extract_retry_delay(error_str)
                    delay = min(delay, 45)  # cap at 45 seconds
                    if attempt < 2:
                        time.sleep(delay)
                        continue
                    else:
                        break  # try next model
                else:
                    # Other error — try next model
                    break

    # All models failed
    raise last_error or Exception("all models unavailable")


def _generate_title(user_message):
    """Generate a short title from the user's first message (no API call)."""
    # Clean up and truncate
    title = user_message.strip()
    # Remove common filler words at start
    for prefix in ["hey ", "yo ", "hi ", "hello ", "sup ", "ok so ", "so ", "um ", "like "]:
        if title.lower().startswith(prefix):
            title = title[len(prefix):]
            break
    title = title.strip()
    if len(title) > 35:
        # Cut at last word boundary
        title = title[:35].rsplit(" ", 1)[0] + "..."
    return title or "chat"


def send_message(username, chat_id, message):
    profile = load_profile(username)
    profile["chat_count"] = profile.get("chat_count", 0) + 1
    save_profile(username, profile)

    chat_data = load_chat(username, chat_id)
    if not chat_data:
        return "chat not found"

    profile_text = profile_to_text(profile)
    system = SYSTEM_PROMPT.format(user_profile=profile_text)

    # Build context from this chat's history
    contents = []
    for msg in chat_data["messages"][-30:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["text"])]))

    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    # Call with retry + fallback
    reply = _call_gemini(contents, system)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_data["messages"].append({"role": "user", "text": message, "time": now})
    chat_data["messages"].append({"role": "bot", "text": reply, "time": now})

    # Auto-title from first message (no API call)
    if chat_data.get("title") == "new chat" and len(chat_data["messages"]) <= 2:
        chat_data["title"] = _generate_title(message)

    if len(chat_data["messages"]) > 500:
        chat_data["messages"] = chat_data["messages"][-500:]

    _save_chat(username, chat_data)
    update_profile_from_chat(username, message, reply)

    return reply
