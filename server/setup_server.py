"""Apply layout.py to a Discord server.

    python setup_server.py           # dry run: prints what would change
    python setup_server.py --apply   # actually does it

Needs DISCORD_TOKEN and GUILD_ID in .env (see .env.example). Never deletes
anything: channels and roles that aren't in layout.py are listed and left alone.
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

import layout

sys.stdout.reconfigure(encoding="utf-8")


def slug(name: str) -> str:
    """'💬・general' -> 'general', '🎮 Squad I' -> 'squadi'."""
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find(items, spec):
    """Match by the layout name first, then by any old names listed under "was"."""
    for name in [spec["name"], *spec.get("was", [])]:
        target = slug(name)
        hit = next((i for i in items if slug(i.name) == target), None)
        if hit is not None:
            return hit
    return None


def layout_channels():
    for cat_spec in layout.CATEGORIES:
        yield from cat_spec["channels"]


class Makeover:
    def __init__(self, guild: discord.Guild, apply: bool):
        self.guild = guild
        self.apply = apply
        self.roles: dict[str, discord.Role] = {}
        self.channels: dict[str, discord.abc.GuildChannel] = {}
        self.touched: set[int] = set()
        self.order: list[tuple] = []  # (category, [channels]) in layout order
        self.system_channel = None
        self.afk_channel = None

    async def do(self, verb, what, action):
        print(f"  {verb:<7} {what}")
        if self.apply:
            return await action()
        return None

    # ------------------------------------------------------------ checks
    def preflight(self) -> bool:
        me = self.guild.me
        if not me.guild_permissions.administrator:
            print("! The bot needs the Administrator permission (it creates an admin role")
            print("  and read-only channels). Re-invite it with the link in the README.")
            return False
        above = [r.name for r in self.guild.roles if r > me.top_role]
        if above:
            print(f"! '{me.top_role.name}' sits below {', '.join('@' + n for n in above)}; those roles")
            print("  can't be touched. Drag it to the very top in Server Settings -> Roles to fix.")
        return True

    # ------------------------------------------------------------ roles
    async def make_roles(self):
        print("\nRoles")
        editable = [r for r in self.guild.roles if not r.managed and not r.is_default()]
        ordered = []
        for spec in layout.ROLES:
            name = spec["name"]
            kwargs = {
                "name": name,
                "colour": discord.Colour(spec.get("color", 0)),
                "hoist": spec.get("hoist", False),
                "mentionable": spec.get("mentionable", False),
            }
            if spec.get("admin"):
                kwargs["permissions"] = discord.Permissions(administrator=True)

            role = find(editable, spec)
            if role is None:
                role = await self.do("create", f"@{name}", lambda: self.guild.create_role(**kwargs))
            elif role >= self.guild.me.top_role:
                print(f"  skip    @{role.name} (above the bot's role)")
            elif any(getattr(role, k) != v for k, v in kwargs.items()):
                was = f" (was @{role.name})" if role.name != name else ""
                role = await self.do("update", f"@{name}{was}", lambda: role.edit(**kwargs)) or role
            else:
                print(f"  ok      @{name}")

            if role is not None:
                self.roles[name] = role
                self.touched.add(role.id)
                if role < self.guild.me.top_role:
                    ordered.append(role)

        if not self.apply:
            print("  order   stack roles in layout order under the bot's role")
        elif ordered:
            # Positions shift as roles are created, so ask Discord for the current ones.
            fresh = {r.id: r for r in await self.guild.fetch_roles()}
            top = fresh[self.guild.me.top_role.id].position - 1
            await self.guild.edit_role_positions({role: top - i for i, role in enumerate(ordered)})
            print("  order   roles stacked in layout order")

    # ------------------------------------------------------------ channels
    def read_only_overwrites(self):
        ow = {
            self.guild.default_role: discord.PermissionOverwrite(
                send_messages=False,
                create_public_threads=False,
                create_private_threads=False,
                add_reactions=True,
            ),
            self.guild.me: discord.PermissionOverwrite(send_messages=True, embed_links=True),
        }
        if "Keeper" in self.roles:
            ow[self.roles["Keeper"]] = discord.PermissionOverwrite(send_messages=True)
        return ow

    async def make_channels(self):
        for cat_spec in layout.CATEGORIES:
            name = cat_spec["name"]
            print(f"\n{name.upper()}")
            cat = find(self.guild.categories, cat_spec)
            if cat is None:
                cat = await self.do("create", f"category {name}", lambda: self.guild.create_category(name))
            elif cat.name != name:
                cat = await self.do("rename", f"category {name} (was {cat.name})", lambda: cat.edit(name=name)) or cat
            if cat is not None:
                self.touched.add(cat.id)

            members = []
            for spec in cat_spec["channels"]:
                ch = await self.make_channel(spec, cat)
                if ch is None:
                    continue
                members.append(ch)
                self.touched.add(ch.id)
                self.channels[slug(spec["name"])] = ch
                if spec.get("system"):
                    self.system_channel = ch
                if spec.get("afk"):
                    self.afk_channel = ch
            if cat is not None:
                self.order.append((cat, members))

    async def make_channel(self, spec, cat):
        name = spec["name"]
        voice = spec.get("type") == "voice"
        pool = self.guild.voice_channels if voice else self.guild.text_channels
        label = name if voice else f"#{name}"

        kwargs = {"name": name}
        if voice:
            kwargs["user_limit"] = spec.get("user_limit", 0)
        else:
            kwargs["topic"] = spec.get("topic", "")
            kwargs["slowmode_delay"] = spec.get("slowmode", 0)

        ch = find(pool, spec)
        if ch is None:
            if spec.get("read_only"):
                kwargs["overwrites"] = self.read_only_overwrites()
            create = self.guild.create_voice_channel if voice else self.guild.create_text_channel
            return await self.do("create", label, lambda: create(category=cat, **kwargs))

        changed = [k for k, v in kwargs.items() if (getattr(ch, k, v) or type(v)()) != v]
        if spec.get("read_only") and ch.overwrites_for(self.guild.default_role).send_messages is not False:
            kwargs["overwrites"] = self.read_only_overwrites()
            changed.append("read-only perms")
        if cat is None or ch.category_id != cat.id:
            changed.append("category")
            if cat is not None:
                kwargs["category"] = cat
        if not changed:
            print(f"  ok      {label}")
            return ch

        was = f" (was {ch.name})" if ch.name != name else ""
        what = f"{label}{was}: {', '.join(c.replace('_', ' ') for c in changed)}"
        return await self.do("update", what, lambda: ch.edit(**kwargs)) or ch

    async def arrange(self):
        """Layout categories go to the top, channels in layout order."""
        print("\nOrder")
        if not self.apply:
            print("  move    layout categories to the top, channels in layout order")
            return
        await asyncio.sleep(2)  # let the gateway deliver the channels we just created

        def fresh(c):
            return self.guild.get_channel(c.id) or c

        prev_cat = None
        for cat, members in self.order:
            cat = fresh(cat)
            if prev_cat is None:
                await cat.move(beginning=True)
            else:
                await cat.move(after=prev_cat)
            prev_cat = cat
            prev = {}
            for ch in map(fresh, members):
                if ch.type not in prev:
                    await ch.move(beginning=True, category=cat, sync_permissions=False)
                else:
                    await ch.move(after=prev[ch.type], category=cat, sync_permissions=False)
                prev[ch.type] = ch
        print("  move    done")

    # ------------------------------------------------------------ server
    async def server_settings(self):
        print("\nServer")
        kwargs = {}
        if any(s.get("system") for s in layout_channels()):
            kwargs["system_channel"] = self.system_channel
        if any(s.get("afk") for s in layout_channels()):
            kwargs["afk_channel"] = self.afk_channel
            kwargs["afk_timeout"] = layout.AFK_TIMEOUT_SECONDS
        if layout.ICON_PATH:
            kwargs["icon"] = Path(layout.ICON_PATH).read_bytes()
        if kwargs:
            what = ", ".join(k.replace("_", " ") for k in kwargs)
            await self.do("update", what, lambda: self.guild.edit(**kwargs))

    # ------------------------------------------------------------ posts
    def expand(self, text: str) -> str:
        """{#general} -> clickable channel link, {@Squad} -> role mention."""

        def chan(m):
            ch = self.channels.get(slug(m.group(1)))
            return ch.mention if ch else f"#{m.group(1)}"

        def role(m):
            r = self.roles.get(m.group(1))
            return r.mention if r else f"@{m.group(1)}"

        text = re.sub(r"\{#([^}]+)\}", chan, text)
        return re.sub(r"\{@([^}]+)\}", role, text)

    async def make_posts(self):
        print("\nPosts")
        for spec in layout_channels():
            key = spec.get("post")
            if not key:
                continue
            ch = self.channels.get(slug(spec["name"]))
            if ch is not None and self.guild.get_channel(ch.id) is not None:
                if [m async for m in ch.history(limit=50) if m.author == self.guild.me]:
                    print(f"  ok      {key} (already posted in #{ch.name})")
                    continue
            post = layout.POSTS[key]
            embed = discord.Embed(
                title=post["title"],
                description=self.expand(post["description"]),
                colour=layout.FOREST,
            )
            if post.get("footer"):
                embed.set_footer(text=post["footer"])
            await self.do("post", f"{key} -> #{spec['name']}", lambda: ch.send(embed=embed))

    def report_untouched(self):
        channels = [c for c in self.guild.channels if c.id not in self.touched]
        roles = [
            r for r in self.guild.roles
            if r.id not in self.touched and not r.is_default() and not r.managed
        ]
        if channels or roles:
            print("\nLeft alone (not in layout.py; delete or move them by hand if you want):")
            for c in channels:
                print(f"  - {c.type.name:<8} {c.name}")
            for r in roles:
                print(f"  - role     @{r.name}")

    async def run(self) -> bool:
        mode = "APPLYING" if self.apply else "DRY RUN (nothing changes; add --apply to do it)"
        print(f"{self.guild.name}: {mode}")
        if not self.preflight():
            return False
        await self.make_roles()
        await self.make_channels()
        await self.arrange()
        await self.server_settings()
        await self.make_posts()
        self.report_untouched()
        print("\nDone." if self.apply else "\nThat's the plan. Run again with --apply.")
        return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="make the changes (default is a dry run)")
    args = parser.parse_args()

    load_dotenv(Path(__file__).with_name(".env"))
    token = os.getenv("DISCORD_TOKEN")
    guild_id = os.getenv("GUILD_ID")
    if not token or not guild_id:
        sys.exit("Set DISCORD_TOKEN and GUILD_ID in server/.env (copy .env.example).")

    client = discord.Client(intents=discord.Intents.default())
    result = {"ok": False}

    @client.event
    async def on_ready():
        try:
            guild = client.get_guild(int(guild_id))
            if guild is None:
                print(f"The bot isn't in server {guild_id}. Invite it with:")
                print(
                    f"  https://discord.com/oauth2/authorize?client_id={client.application_id}"
                    "&scope=bot&permissions=8"
                )
                return
            result["ok"] = await Makeover(guild, args.apply).run()
        except discord.HTTPException as e:
            print(f"\nDiscord refused a change: {e}")
        finally:
            await client.close()

    client.run(token, log_handler=None)
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
