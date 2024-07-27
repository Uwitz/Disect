import re

from discord import Message, WebhookMessage
from discord import Webhook
from discord.ext.commands import Cog

from typing import List
from aiohttp import ClientSession

def _clean_message(message: str) -> str:
    return re.sub(r'@(everyone|here|[!&]?[0-9]{17,21})', '@\u200b\\1', message)

class Sync(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_message")
    async def message_sync(self, message: Message):
        if message.author.bot: return
        current_guild_config = await self.bot.chatsync_db["config"].find_one(
            {
                "_id": message.guild.id
            }
        )
        if current_guild_config.get("linked") and message.channel.id == current_guild_config.get("sync_channel"):
            guild_config_list: List[dict] = self.bot.chatsync_db["config"].find(
                {
                    "linked": True
                }
            )
            message_content = _clean_message(message.content)
            message_data = {
                "_id": message.id,
                "message_author": {
                    "id": message.author.id,
                    "username": message.author.display_name,
                    "name": message.author.name,
                    "avatar_icon": message.author.display_avatar.url
                },
                "content": message.content,
                "guild_messages": {
                    f"{message.guild.id}": message.id
                },
                "attachments": message.attachments
            }
            async with ClientSession() as session:
                async for guild in guild_config_list:
                    if guild.get("_id") != message.guild.id:
                        webhook = Webhook.from_url(
                            guild.get("sync_webhook"),
                            session = session
                        )
                        webhook_message: WebhookMessage = await webhook.send(
                            username = f"{message.author.display_name} ({message.guild.name})",
                            avatar_url = message.author.display_avatar.url,
                            content = message_content,
                            # files = message.attachments,
                            allowed_mentions = False,
                            wait = True
                        )
                        message_data["guild_messages"][f"{guild.get('_id')}"] = webhook_message.id

            await self.bot.chatsync_db["messages"].insert_one(message_data)

    @Cog.listener("on_message_edit")
    async def edit_sync(self, message_before: Message, message_after: Message):
        if message_after.author.bot: return
        current_guild_config = await self.bot.chatsync_db["config"].find_one(
            {
                "_id": message_after.guild.id
            }
        )
        if current_guild_config.get("linked") and message_after.channel.id == current_guild_config.get("sync_channel"):
            guild_config_list: List[dict] = self.bot.chatsync_db["config"].find(
                {
                    "linked": True
                }
            )
            original_message = await self.bot.chatsync_db["messages"].find_one(
                {
                    "_id": message_after.id
                }
            )
            guild_messages = original_message.get("guild_messages")
            async with ClientSession() as session:
                async for guild in guild_config_list:
                    if guild.get("_id") == message_after.guild.id: continue
                    webhook = Webhook.from_url(
                        guild.get("sync_webhook"),
                        session = session
                    )
                    await webhook.edit_message(guild_messages[f"{guild.get("_id")}"], content = message_after.content)
            await self.bot.chatsync_db["messages"].update_one(
                {
                    "_id": message_after.id
                },
                {
                    "$set": {
                        "content": message_after.content
                    }
                }
            )

async def setup(bot):
    await bot.add_cog(Sync(bot))