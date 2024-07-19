import os

from discord import Member
from discord.ext.commands import Bot, Cog

from discord import Button, ButtonStyle, Embed, Interaction, Member, TextChannel
from discord.ui import View, button
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
	async def ban(self, interaction: Interaction, button: Button):
		try:
			await self.target_user.ban(
				reason = self.reason,
				delete_message_seconds = 60
			)
		except:
			return await interaction.response.send_message(f"{os.getenv('EMOJI_FAIL')} Insufficient permissions to ban user.")
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
	async def infractions(self, interaction: Interaction, button: Button):
		...

	@button(
		label = "Release",
		style = ButtonStyle.grey
	)
		...
	async def cancel(self, interaction: Interaction, button: Button):

class GlobalModeration(Cog):
	def __init__(self, bot: Bot):
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

		if guild_config.get("moderation").get("auto_ban"):
			if member_record.get("infractions").get("global_ban").get("banned"):
				await member.ban(reason = member_record.get("infractions").get("global_ban").get("reason"))

			else:
				return

		else:
			report_channel = self.bot.get_channel(guild_config.get("moderation").get("request_channel"))
			report_embed = Embed(
				description = f"This member has been banned Federation-wide for:\n```diff\n-{member_record.get('infractions').get('global_ban_reason')}",
				colour = 0x2B2D31
			)
			return await report_channel.send(
				embed = report_embed,
				view = WarningPrompt(
					target_user = member,
					record = member_record,
					reason = member_record.get("infractions").get("global_ban").get("reason")
				)
			)

async def setup(bot: Bot):
	await bot.add_cog(GlobalModeration(bot))