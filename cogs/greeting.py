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
    async def onboard_completion(self, member: Member):
        member_record: dict | None = await self.bot.database["members"].find_one(
            {
                "_id": member.id
            }
        )
        server_config: dict | None = await self.bot.database["config"].find_one(
            {
                "_id": member.guild.id
            }
        )
        
        if (int(member.created_at.timestamp()) > int(datetime.now().timestamp()) - 2592000) and not member_record.get("bypass").get(f"{member.guild.id}"):
            while member.pending:
                asyncio.sleep(0.5)
                continue

            disabled_role: Role = member.guild.get_role(int(server_config.get("roles").get("disabled")))
            reletive_timestamp = (
                int(datetime.now().timestamp()) + (
                    (
                        (int(datetime.now().timestamp()) - 2592000) - int(member.created_at.timestamp())
                    )
                )
            )
            embed = Embed(
                timestamp = datetime.now(),
                description = f"Your account is too new, therefore not trusted to participate and interact with the discord server.\nThis is to prevent spam accounts joining our Discord Server, please rejoin <t:{reletive_timestamp}:R>.\n\nIf you'd like to join the discord server regardless of this restriction, please email us at `border@uwitz.org` with your Discord ID.",
                colour = 0xFF7979
            ).set_author(
                name = "Disabled Account",
                icon_url = "https://i.ibb.co/rdDr0Pq/cancel.png"
            ).set_footer(
                text = member.guild.name,
                icon_url = member.guild.icon.url
            )
            await member.send(embed = embed)
            await member.add_roles(disabled_role, reason = "Disabled User from interacting with Server.")

        else:
            if ((not member.pending) and not server_config.get("roles").get("disabled") in [role.id for role in member.roles]):
                if server_config.get("join_greeting"):
                    embed = Embed(
                        timestamp = datetime.now(),
                        description = random.choice(
                            [
                                f"Welcome to the {member.guild.name} <@!{member.id}>!",
                                f"We hope you have a nice stay <@!{member.id}>",
                                f"Make yourself at home <@!{member.id}>! *(with the rules in mind that is)*",
                                f"Welcome to {member.guild.name} <@!{member.id}>!"
                            ]
                        ),
                        colour = 0x2B2D31
                    ).set_author(
                        name = random.choice(
                            [
                                f"{member.name.capitalize()} Joined!",
                                f"Welcome {member.name.capitalize()}!",
                                f"{member.name.capitalize()} Entered!",
                                f"{member.name.capitalize()} Landed",
                                f"{member.name.capitalize()} crossed the border",
                                f"Welcome onboard {member.name.capitalize()}!"
                            ]
                        ),
                        icon_url = member.display_avatar.url
                    ).set_footer(
                        text = member.guild.name,
                        icon_url = member.guild.icon.url
                    )
                    await member.guild.system_channel.send(embed = embed)
                member_role: Role = member.guild.get_role(server_config.get("roles").get("member"))
                await member.add_roles(member_role, reason = "Onboard Completed")

async def setup(bot):
    await bot.add_cog(Greeting(bot))