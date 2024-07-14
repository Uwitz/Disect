import os

from discord import Member
from discord.ext.commands import Cog

from discord import Button, ButtonStyle, Embed, Interaction, Member, TextChannel
from discord.ui import View, button
from discord.app_commands import command, describe
from discord.ext.commands import Cog

class WarningPrompt(View):
	def __init__(self, target_user: Member, member_record: dict, reason: str):
		self.target_user = target_user
		self.member_record = member_record
		self.reason = reason
		super().__init__(timeout = None)

	@button(
		label = "Ban",
		style = ButtonStyle.red
	)
	async def ban(self, button: Button, interaction: Interaction):
		try:
			await self.target_user.ban(
				reason = self.reason,
				delete_message_seconds = 60
			)
		except:
			return await interaction.response.send_message(f"{os.getenv('EMOJI_FAIL')} You are not authorised to ban this user.")
		button.disabled = True
		button.style = ButtonStyle.green
		for button_ in self.children:
			button_.disabled = True

		await interaction.edit_original_response(
			embed = self.original_embed.add_field(
				name = "Authorised by:",
				value = f"<@!{interaction.user.id}>"
			),
			view = self
		)

	@button(
		label = "Infractions",
		style = ButtonStyle.blurple
	)
	async def infractions(self, button: Button, interaction: Interaction):
		...

	@button(
		label = "Release",
		style = ButtonStyle.grey
	)
	async def cancel(self, button: Button, interaction: Interaction):
		...

class GlobalModeration(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener("on_member_join")
	async def ban_check(self, member: Member):
		member_record: dict | None = await self.bot.database["members"].find_one(
			{
				"_id": member.id
			}
		)
		guild_config: dict | None = await self.bot.database["config"].find_one(
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
				description = f"This member has been banned Federation-wide for:\n```diff\n-{member_record.get('global_ban_reason')}",
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

async def setup(bot):
	await bot.add_cog(GlobalModeration(bot))