"""The server layout. Edit this file, then run setup_server.py.

Existing channels/roles are matched by their plain name (emoji and
separators ignored), so an old "#general" becomes "💬・general" instead
of getting a duplicate. Anything not listed here is left alone.
"""

# Field Notebook palette (lscaturchio.xyz DESIGN.md)
FOREST = 0x42A979  # forest-ink, night variant: the one pen
MOSS = 0x397F5E
SAND = 0xE2DBD5
MUTED = 0xABB0BA
SLATE = 0x606976

# ---------------------------------------------------------------- games
# One ping role + one text channel per game. Change these to what your
# group actually plays.
GAMES = [
    # (emoji, channel name, role name)
    ("🎯", "valorant", "Valorant"),
    ("⛏️", "minecraft", "Minecraft"),
    ("🚀", "rocket-league", "Rocket League"),
    ("🪖", "fortnite", "Fortnite"),
]

# ---------------------------------------------------------------- roles
# Top to bottom. Only Keeper and Squad get a name colour (the One Pen Rule:
# colour marks what matters, it isn't wallpaper). Game roles are colourless
# ping roles.
ROLES = [
    {"name": "Keeper", "color": FOREST, "hoist": True, "admin": True},
    {"name": "Squad", "color": MOSS, "hoist": True},
    {"name": "Guest", "color": MUTED},
    {"name": "Bots", "color": SLATE, "hoist": True},
    {"name": "LFG", "mentionable": True},
    *({"name": role, "mentionable": True} for _, _, role in GAMES),
]

# ---------------------------------------------------------------- channels
# Categories are numbered like a catalogue; Discord uppercases them, which
# gives you the site's wall-label look for free.
# "read_only": everyone can read and react, only Keepers (and the bot) post.
CATEGORIES = [
    {
        "name": "01 · front desk",
        "channels": [
            {"name": "📌・rules", "topic": "Read these once. They're short.", "read_only": True, "post": "rules"},
            {"name": "📣・announcements", "topic": "Game nights, updates, server news.", "read_only": True},
            {"name": "👋・welcome", "topic": "New faces land here.", "read_only": True, "system": True, "post": "welcome"},
        ],
    },
    {
        "name": "02 · the lobby",
        "channels": [
            {"name": "💬・general", "topic": "Anything goes. Mostly."},
            {"name": "🤣・memes", "topic": "Post it here, not in #general."},
            {"name": "📸・clips", "topic": "Highlights, fails, and receipts.", "slowmode": 10},
            {"name": "🔗・links", "topic": "Videos, articles, deals, patch notes."},
            {"name": "🤖・bot-commands", "topic": "Keep the bot spam in one place."},
        ],
    },
    {
        "name": "03 · games",
        "channels": [
            {"name": "🎮・lfg", "topic": "Looking for group? Ping @LFG here."},
            *(
                {"name": f"{emoji}・{channel}", "topic": f"{role} talk, squads, and strats. Ping @{role}."}
                for emoji, channel, role in GAMES
            ),
        ],
    },
    {
        "name": "04 · voice",
        "channels": [
            {"name": "🔊 Lobby", "type": "voice"},
            {"name": "🎮 Squad I", "type": "voice", "user_limit": 5},
            {"name": "🎮 Squad II", "type": "voice", "user_limit": 5},
            {"name": "🎧 Chill", "type": "voice"},
            {"name": "💤 AFK", "type": "voice", "afk": True},
        ],
    },
]

AFK_TIMEOUT_SECONDS = 900  # 1, 5, 15, 30 or 60 minutes are the allowed values

# Optional: path to a square PNG/JPG to use as the server icon.
ICON_PATH = None

# ---------------------------------------------------------------- posts
# Embeds the bot posts once (skipped if the bot already posted there).
# {#general} becomes a clickable channel link and {@Squad} a role mention.
POSTS = {
    "rules": {
        "title": "House rules",
        "description": "\n".join(
            [
                "`01`  Be decent. Trash-talk the play, not the person.",
                "`02`  No cheats, no exploits, no account drama.",
                "`03`  Clips in {#clips}, memes in {#memes}.",
                "`04`  Spoilers go under ||spoiler tags||.",
                "`05`  Want a squad? Ping {@LFG} in {#lfg}, not @everyone.",
                "`06`  Keepers have the final word.",
            ]
        ),
        "footer": "FRONT DESK · 01",
    },
    "welcome": {
        "title": "Welcome in",
        "description": "\n".join(
            [
                "Read {#rules}, then say hi in {#general}.",
                "",
                "**Roles**",
                "{@Keeper}  runs the place",
                "{@Squad}  the regulars",
                "`GAME ROLES`  pings for a specific game: ask a Keeper to add yours",
            ]
        ),
        "footer": "FRONT DESK · 03",
    },
}
