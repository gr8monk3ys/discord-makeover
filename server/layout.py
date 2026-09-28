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
    ("🪖", "wardogs", "Wardogs"),
    ("⛏️", "minecraft", "Minecraft"),
]

# Any role, category or channel can list old names under "was": the existing
# one is renamed and restyled in place, so members, messages and permissions
# carry over instead of ending up with a duplicate.

# ---------------------------------------------------------------- roles
# Top to bottom. Only Keeper and Squad get a name colour (the One Pen Rule:
# colour marks what matters, it isn't wallpaper). Game roles are colourless
# ping roles.
ROLES = [
    {"name": "Keeper", "color": FOREST, "hoist": True, "admin": True, "was": ["Admin"]},
    {"name": "Moderator", "keep": True},
    {"name": "Squad", "color": MOSS, "hoist": True, "was": ["Member"]},
    {"name": "Guest", "color": MUTED},
    {"name": "Bots", "color": SLATE, "hoist": True, "was": ["Bot"]},
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
        "was": ["Welcome"],
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
        ],
    },
    {
        "name": "03 · games",
        "channels": [
            {"name": "🕹️・gaming", "topic": "General gaming chat.", "was": ["gaming"]},
            {"name": "🎮・lfg", "topic": "Looking for group? Ping @LFG here."},
            *(
                {"name": f"{emoji}・{channel}", "topic": f"{role} talk, squads, and strats. Ping @{role}."}
                for emoji, channel, role in GAMES
            ),
        ],
    },
    {
        "name": "04 · off topic",
        "channels": [
            {"name": "🎨・art", "topic": "Things you made."},
            {"name": "💻・code", "topic": "Projects, snippets, and bugs."},
            {"name": "👗・fashion", "topic": "Fits and finds."},
            {"name": "♟️・chess", "topic": "Games, puzzles, and challenges."},
        ],
    },
    {
        "name": "05 · voice",
        "was": ["Voice Channels"],
        "channels": [
            {"name": "🔊 Lobby", "type": "voice", "was": ["General"]},
            {"name": "🎮 Squad", "type": "voice", "user_limit": 5, "was": ["🎮 Squad I", "General 2"]},
            {"name": "💤 AFK", "type": "voice", "afk": True},
        ],
    },
    {
        # Staff-only: channels keep their existing permissions.
        "name": "00 · staff",
        "was": ["Admin"],
        "channels": [
            {"name": "🛡️・mod", "was": ["mod"]},
            {"name": "🔒・admin", "was": ["admin"]},
        ],
    },
]

AFK_TIMEOUT_SECONDS = 900  # 1, 5, 15, 30 or 60 minutes are the allowed values

# Optional: path to a square PNG/JPG to use as the server icon (relative to
# this folder). assets/make_icon.py draws the Field Notebook one.
ICON_PATH = "../assets/server-icon.png"

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


# ---------------------------------------------------------------- polish
# Used by polish_server.py: Community, Onboarding, AutoMod, and trimming.

# Empty channels to remove (skipped if anyone has posted in them).
# Small servers feel emptier with more channels: aim for 5-10 text, 2-3 voice.
TRIM = ["🔗・links", "🤖・bot-commands", "🎮 Squad II", "🎧 Chill"]

COMMUNITY = {
    "rules_channel": "📌・rules",
    "updates_channel": "🛡️・mod",  # where Discord sends admin-only notices
}

# Onboarding: what new members see before they land. Channels listed here are
# the defaults everyone gets; Discord needs at least 7, 5 of them postable.
ONBOARDING_DEFAULT_CHANNELS = [
    "📌・rules", "📣・announcements", "👋・welcome", "💬・general",
    "🤣・memes", "📸・clips", "🕹️・gaming", "🎮・lfg",
]
ONBOARDING_PROMPTS = [
    {
        "title": "What do you play?",
        "multi": True,
        "options": [
            *(
                {"title": role, "emoji": emoji, "role": role, "channel": f"{emoji}・{channel}",
                 "description": f"Get @{role} pings and the #{channel} channel."}
                for emoji, channel, role in GAMES
            ),
            {"title": "Ping me for squads", "emoji": "🎮", "role": "LFG",
             "description": "Get @LFG pings when someone needs a squad."},
        ],
    },
]

# AutoMod: alerts go to this channel; these roles are never filtered.
AUTOMOD_ALERTS = "🛡️・mod"
AUTOMOD_EXEMPT_ROLES = ["Keeper", "Moderator"]
MENTION_LIMIT = 6
