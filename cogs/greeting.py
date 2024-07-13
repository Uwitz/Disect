import os
import random
import asyncio

from discord import Embed, Member, Role
from discord.ext.commands import Cog

from datetime import datetime

class Greeting(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_member_join")
    async def join_event(self, member: Member):
        if int(member.created_at.timestamp()) > int(datetime.now().timestamp()) - 2592000:
            while member.pending:
                asyncio.sleep(0.5)
                continue
            disabled_role: Role = member.guild.get_role(int(os.getenv("DISABLED_ROLE")))
            reletive_timestamp = (
                int(datetime.now().timestamp()) + (
                    (
                        (int(datetime.now().timestamp()) - 2592000) - int(member.created_at.timestamp())
                    )
                )
            )
            embed = Embed(
                timestamp = datetime.now(),
                description = f"Your account is too new, therefore not trusted to participate and interact with the discord server.\nThis is to prevent spam accounts joining our Discord Server, please rejoin <t:{reletive_timestamp}:R>.\n\nIf you'd like to join the discord server regardless of this restriction, please email us at `border@snyco.uk` with your Discord ID.",
                colour = 0xFF7979
            ).set_author(
                name = "Disabled Account",
                icon_url = "https://i.ibb.co/rdDr0Pq/cancel.png"
            ).set_footer(
                text = "Snyco's World",
                icon_url = member.guild.icon.url
            )
            await member.send(embed = embed)
            await member.add_roles(disabled_role, reason = "Disabled User from interacting with Server.")

    @Cog.listener("on_member_update")
    async def onboard_completion(self, member_before: Member, member_after: Member):
        if (member_before.pending and not member_after.pending and not os.getenv("DISABLED_ROLE") in [role.id for role in member_after.roles]):
            embed = Embed(
                timestamp = datetime.now(),
                description = random.choice(
                    [
                        f"Welcome to the world of Snyco <@!{member_after.id}>!",
                        f"We hope you have a nice stay <@!{member_after.id}>",
                        f"Make yourself at home <@!{member_after.id}>! *(with the rules in mind that is)*",
                        f"Welcome to Snyco's world <@!{member_after.id}>!"
                    ]
                ),
                colour = 0xFF7A7B
            ).set_author(
                name = random.choice(
                    [
                        f"{member_after.name.capitalize()} Joined!",
                        f"Welcome {member_after.name.capitalize()}!",
                        f"{member_after.name.capitalize()} Entered!",
                        f"{member_after.name.capitalize()} Landed",
                        f"{member_after.name.capitalize()} crossed the border"
                    ]
                ),
                icon_url = member_after.display_avatar.url
            ).set_footer(
                text = "Snyco's World",
                icon_url = member_after.guild.icon.url
            )
            await member_after.guild.system_channel.send(embed = embed)
            member_role: Role = member_after.guild.get_role(int(os.getenv("MEMBER_ROLE")))
            await member_after.add_roles(member_role, reason = "Onboard Completed")

async def setup(bot):
    await bot.add_cog(Greeting(bot))