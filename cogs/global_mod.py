import os

from discord import Member
from discord.ext.commands import Cog

from discord import Button, ButtonStyle, Embed, Interaction, Member, TextChannel
from discord.ui import View, button
from discord.app_commands import command, describe
from discord.ext.commands import Cog
class GlobalModeration(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener("on_member_join")
	async def ban_check(self, member: Member):
		member_record = await self.bot.database["members"].find_one(
			{
				"_id": member.id
			}
		)
		guild_config = await self.bot.database["config"].find_one(
			{
				"_id": member.guild.id
			}
		)

		if guild_config.get("auto_ban"):
			if member_record.get("global_ban"):
				await member.ban(reason = member_record.get("global_ban_reason"))

			else:
				return

		else:
			report_channel = self.bot.get_channel(guild_config.get("moderation").get("warning_channel"))
			report_embed = Embed(
				description = f"This member has been banned Federation-wide for:\n```diff\n-{member_record.get("global_ban_reason")}",
				colour = 0x2B2D31
			)
			return await report_channel.send(
				embed = report_embed,
				view = WarningPrompt(
					target_user = member,
					record = member_record,
					reason = member_record.get("global_ban_reason")
				)
			)