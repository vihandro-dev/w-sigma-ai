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

    # Detect interests — comprehensive list
    interest_triggers = {
        # Games
        "minecraft": "Minecraft",
        "fortnite": "Fortnite",
        "roblox": "Roblox",
        "valorant": "Valorant",
        "apex legends": "Apex Legends",
        "apex": "Apex Legends",
        "cod": "Call of Duty",
        "call of duty": "Call of Duty",
        "warzone": "Warzone",
        "overwatch": "Overwatch",
        "league of legends": "League of Legends",
        "league": "League of Legends",
        "genshin": "Genshin Impact",
        "genshin impact": "Genshin Impact",
        "honkai": "Honkai Star Rail",
        "gta": "GTA",
        "grand theft auto": "GTA",
        "elden ring": "Elden Ring",
        "zelda": "Zelda",
        "mario": "Mario",
        "smash bros": "Smash Bros",
        "super smash": "Smash Bros",
        "pokemon": "Pokemon",
        "palworld": "Palworld",
        "lethal company": "Lethal Company",
        "among us": "Among Us",
        "rocket league": "Rocket League",
        "fifa": "FIFA/EA FC",
        "ea fc": "FIFA/EA FC",
        "madden": "Madden",
        "2k": "NBA 2K",
        "nba 2k": "NBA 2K",
        "counter strike": "Counter-Strike",
        "csgo": "Counter-Strike",
        "cs2": "Counter-Strike 2",
        "rainbow six": "Rainbow Six Siege",
        "r6": "Rainbow Six Siege",
        "destiny": "Destiny",
        "halo": "Halo",
        "terraria": "Terraria",
        "stardew": "Stardew Valley",
        "stardew valley": "Stardew Valley",
        "animal crossing": "Animal Crossing",
        "dead by daylight": "Dead by Daylight",
        "dbd": "Dead by Daylight",
        "pubg": "PUBG",
        "fall guys": "Fall Guys",
        "brawl stars": "Brawl Stars",
        "clash royale": "Clash Royale",
        "clash of clans": "Clash of Clans",
        "candy crush": "Candy Crush",
        "geometry dash": "Geometry Dash",
        "stumble guys": "Stumble Guys",
        "blox fruits": "Blox Fruits",

        # Anime / Manga
        "anime": "anime",
        "manga": "manga",
        "naruto": "Naruto",
        "one piece": "One Piece",
        "jujutsu": "Jujutsu Kaisen",
        "jjk": "Jujutsu Kaisen",
        "demon slayer": "Demon Slayer",
        "attack on titan": "Attack on Titan",
        "aot": "Attack on Titan",
        "my hero academia": "My Hero Academia",
        "mha": "My Hero Academia",
        "dragon ball": "Dragon Ball",
        "dbz": "Dragon Ball Z",
        "spy x family": "Spy x Family",
        "chainsaw man": "Chainsaw Man",
        "solo leveling": "Solo Leveling",
        "hunter x hunter": "Hunter x Hunter",
        "hxh": "Hunter x Hunter",
        "death note": "Death Note",
        "fullmetal alchemist": "Fullmetal Alchemist",
        "fma": "Fullmetal Alchemist",
        "tokyo ghoul": "Tokyo Ghoul",
        "mob psycho": "Mob Psycho 100",
        "one punch man": "One Punch Man",
        "bleach": "Bleach",
        "black clover": "Black Clover",
        "haikyuu": "Haikyuu",
        "blue lock": "Blue Lock",
        "frieren": "Frieren",
        "oshi no ko": "Oshi no Ko",
        "dandadan": "Dandadan",
        "kaiju no 8": "Kaiju No. 8",
        "bocchi": "Bocchi the Rock",
        "mushoku tensei": "Mushoku Tensei",

        # Music Artists
        "taylor swift": "Taylor Swift",
        "drake": "Drake",
        "travis scott": "Travis Scott",
        "kanye": "Kanye West",
        "ye": "Kanye West",
        "kendrick": "Kendrick Lamar",
        "kendrick lamar": "Kendrick Lamar",
        "sza": "SZA",
        "doja cat": "Doja Cat",
        "olivia rodrigo": "Olivia Rodrigo",
        "billie eilish": "Billie Eilish",
        "bad bunny": "Bad Bunny",
        "the weeknd": "The Weeknd",
        "post malone": "Post Malone",
        "ariana grande": "Ariana Grande",
        "lil uzi": "Lil Uzi Vert",
        "playboi carti": "Playboi Carti",
        "carti": "Playboi Carti",
        "21 savage": "21 Savage",
        "metro boomin": "Metro Boomin",
        "future": "Future",
        "lil baby": "Lil Baby",
        "tyler the creator": "Tyler, The Creator",
        "frank ocean": "Frank Ocean",
        "steve lacy": "Steve Lacy",
        "ice spice": "Ice Spice",
        "nicki minaj": "Nicki Minaj",
        "bts": "BTS",
        "blackpink": "BLACKPINK",
        "stray kids": "Stray Kids",
        "newjeans": "NewJeans",
        "kpop": "K-Pop",
        "k-pop": "K-Pop",
        "jpop": "J-Pop",
        "j-pop": "J-Pop",
        "sabrina carpenter": "Sabrina Carpenter",
        "chappell roan": "Chappell Roan",
        "tyla": "Tyla",

        # Social Media / Platforms
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "instagram": "Instagram",
        "insta": "Instagram",
        "snapchat": "Snapchat",
        "snap": "Snapchat",
        "twitter": "Twitter/X",
        "discord": "Discord",
        "reddit": "Reddit",
        "twitch": "Twitch",
        "pinterest": "Pinterest",
        "bereal": "BeReal",
        "threads": "Threads",
        "spotify": "Spotify/music",
        "apple music": "Apple Music",
        "netflix": "Netflix",
        "hulu": "Hulu",
        "disney plus": "Disney+",
        "crunchyroll": "Crunchyroll",
        "kick": "Kick",

        # Sports
        "basketball": "basketball",
        "football": "football",
        "soccer": "soccer",
        "baseball": "baseball",
        "tennis": "tennis",
        "volleyball": "volleyball",
        "swimming": "swimming",
        "track": "track & field",
        "cross country": "cross country",
        "wrestling": "wrestling",
        "gymnastics": "gymnastics",
        "skateboarding": "skateboarding",
        "skiing": "skiing",
        "snowboarding": "snowboarding",
        "surfing": "surfing",
        "nba": "NBA",
        "nfl": "NFL",
        "mls": "MLS",
        "premier league": "Premier League",
        "champions league": "Champions League",
        "f1": "Formula 1",
        "formula 1": "Formula 1",
        "ufc": "UFC",
        "mma": "MMA",

        # Movies / TV / Entertainment
        "marvel": "Marvel",
        "dc": "DC Comics",
        "star wars": "Star Wars",
        "harry potter": "Harry Potter",
        "lord of the rings": "Lord of the Rings",
        "stranger things": "Stranger Things",
        "squid game": "Squid Game",
        "wednesday": "Wednesday",
        "the bear": "The Bear",
        "euphoria": "Euphoria",
        "arcane": "Arcane",

        # Creative / Tech
        "drawing": "drawing/art",
        "painting": "painting",
        "digital art": "digital art",
        "photography": "photography",
        "coding": "coding",
        "programming": "programming",
        "python": "Python",
        "javascript": "JavaScript",
        "web dev": "web development",
        "game dev": "game development",
        "music production": "music production",
        "beatmaking": "beatmaking",
        "singing": "singing",
        "guitar": "guitar",
        "piano": "piano",
        "drums": "drums",
        "dance": "dancing",
        "writing": "creative writing",
        "reading": "reading/books",
        "cooking": "cooking",
        "baking": "baking",
        "fashion": "fashion",
        "makeup": "makeup/beauty",
        "fitness": "fitness",
        "gym": "gym/fitness",
        "yoga": "yoga",
        "meditation": "meditation",
        "3d printing": "3D printing",
        "robotics": "robotics",
        "ai": "artificial intelligence",

        # Memes / Culture
        "skibidi": "skibidi toilet lore",
        "mrbeast": "MrBeast",
        "mr beast": "MrBeast",
        "dream smp": "Dream SMP",
        "pewdiepie": "PewDiePie",
        "ishowspeed": "IShowSpeed",
        "speed": "IShowSpeed",
        "kai cenat": "Kai Cenat",
        "adin ross": "Adin Ross",
        "xqc": "xQc",
        "pokimane": "Pokimane",
        "ludwig": "Ludwig",
        "markiplier": "Markiplier",
        "jacksepticeye": "Jacksepticeye",
    }

    for trigger, interest in interest_triggers.items():
        if trigger in msg and interest not in profile["interests"]:
            profile["interests"].append(interest)

    # Detect personal facts from "I am/I'm/my name is" patterns
    fact_triggers = [
        "my name is", "i'm ", "i am ", "i like ", "i love ",
        "my favorite", "my fav ", "i play ", "i watch ",
        "i go to ", "i live in", "my age is", "i'm into",
        "i hate ", "i want to ", "i wanna ", "i need ",
        "my hobby", "my hobbies", "i enjoy ", "i started ",
        "i just got", "i'm learning", "i'm studying",
        "i work ", "i'm working", "my dream ", "my goal ",
        "i'm from ", "my school ", "my class ", "my grade ",
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
