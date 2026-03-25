import json
import os

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")


def get_profile_path(username):
    safe_name = "".join(c for c in username if c.isalnum() or c in "-_").lower()
    return os.path.join(PROFILES_DIR, f"{safe_name}.json")


def load_profile(username):
    path = get_profile_path(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "name": username,
        "interests": [],
        "vibe": "",
        "facts": [],
        "chat_count": 0,
    }


def save_profile(username, profile):
    os.makedirs(PROFILES_DIR, exist_ok=True)
    path = get_profile_path(username)
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


def profile_to_text(profile):
    lines = [f"Name: {profile['name']}"]
    if profile.get("interests"):
        lines.append(f"Interests: {', '.join(profile['interests'])}")
    if profile.get("vibe"):
        lines.append(f"Their vibe: {profile['vibe']}")
    if profile.get("facts"):
        lines.append("Things they've told you:")
        for fact in profile["facts"][-15:]:  # keep last 15 facts
            lines.append(f"  - {fact}")
    lines.append(f"Chat sessions so far: {profile.get('chat_count', 0)}")
    return "\n".join(lines)


def update_profile_from_chat(username, user_message, bot_response):
    """Auto-extract personal info from chat to build the profile."""
    profile = load_profile(username)
    msg = user_message.lower()

    # Detect interests
    interest_triggers = {
        "minecraft": "Minecraft",
        "fortnite": "Fortnite",
        "roblox": "Roblox",
        "anime": "anime",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "gaming": "gaming",
        "music": "music",
        "drawing": "drawing/art",
        "basketball": "basketball",
        "football": "football",
        "soccer": "soccer",
        "valorant": "Valorant",
        "apex": "Apex Legends",
        "cod": "Call of Duty",
        "pokemon": "Pokemon",
        "naruto": "Naruto",
        "one piece": "One Piece",
        "jujutsu": "Jujutsu Kaisen",
        "demon slayer": "Demon Slayer",
        "taylor swift": "Taylor Swift",
        "drake": "Drake",
        "travis scott": "Travis Scott",
        "spotify": "Spotify/music",
        "netflix": "Netflix",
        "marvel": "Marvel",
        "skibidi": "skibidi toilet lore",
    }

    for trigger, interest in interest_triggers.items():
        if trigger in msg and interest not in profile["interests"]:
            profile["interests"].append(interest)

    # Detect personal facts from "I am/I'm/my name is" patterns
    fact_triggers = [
        "my name is", "i'm ", "i am ", "i like ", "i love ",
        "my favorite", "my fav ", "i play ", "i watch ",
        "i go to ", "i live in", "my age is", "i'm into",
    ]
    for trigger in fact_triggers:
        if trigger in msg and len(user_message) < 200:
            fact = user_message.strip()
            if fact not in profile["facts"]:
                profile["facts"].append(fact)
                # Cap at 30 facts
                if len(profile["facts"]) > 30:
                    profile["facts"] = profile["facts"][-30:]
            break

    save_profile(username, profile)
