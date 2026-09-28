# Discord makeover: Field Notebook

Your Discord client and server, restyled to match lscaturchio.xyz: night or
paper ground, forest-green ink, Fraunces headings, and IBM Plex Mono wall labels.

## 1. Client theme (`theme/field-notebook.theme.css`)

Works with **Vencord** (recommended) or **BetterDiscord**.

- **Vencord:** Settings → Vencord → Themes → *Open Themes Folder*, drop the file in, then toggle it on.
- **BetterDiscord:** Settings → Themes → *Open Themes Folder*, drop the file in, then toggle it on.

Discord's own **Appearance** setting picks the variant: Dark, Darker or Midnight
gives the night notebook, and Light gives the paper one.

Heads up: both mods break Discord's Terms of Service. Bans for themes alone are
very rare, but it's your call. Discord renames its internal classes every few
months. If a detail stops applying (for example the mono category labels), the
colours and fonts still work because they're driven by CSS variables.

## 2. Server makeover (`server/`)

This is a one-shot bot run. It creates or renames roles, categories and channels,
makes the front-desk channels read-only, sets the join-message and AFK channels,
and posts rules and welcome embeds. It **never deletes** anything. Anything not
in `layout.py` gets listed so you can clean it up by hand.

**One-time setup**

1. Go to <https://discord.com/developers/applications> → **New Application** → **Bot** → **Reset Token**, and copy the token.
2. Copy `.env.example` to `.env` and paste the token and your server ID into it.
3. Invite the bot with Administrator (replace `APP_ID` with the Application ID from the General Information page):
   `https://discord.com/oauth2/authorize?client_id=APP_ID&scope=bot&permissions=8`
4. Server Settings → Roles: drag the bot's role to the **very top**.

**Run it**

```bash
cd server
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python setup_server.py          # dry run: shows the plan
.venv\Scripts\python setup_server.py --apply  # do it
```

Edit `layout.py` first. `GAMES` at the top holds your group's actual games, and
each one gets a ping role plus a channel. The script is safe to re-run: it
matches existing channels and roles by plain name, so `#general` becomes
`#💬・general` instead of a duplicate.

**Afterwards**

- Give yourself **@Keeper** and your friends **@Squad**.
- Kick the bot. It doesn't need to stay, and Admin bots sitting around are a risk.
- Reset the bot token in the portal if you shared `.env` anywhere.
- Optional: set `ICON_PATH` in `layout.py` to a square image for the server icon.
