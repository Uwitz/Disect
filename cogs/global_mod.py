import os

from discord import Member
from discord.ext.commands import Bot, Cog

from discord import Button, ButtonStyle, Embed, Interaction, Member, Role
from discord.ui import View, button
from discord.ext.commands import Cog

class WarningPrompt(View):
	def __init__(
		self,
		bot_object: Bot,
		ban_timestamp: int,
		target_user: Member,
		member_record: dict,
		disabled_role: Role,
		guild_id: int,
		reason: str
	):
		self.bot_object = bot_object
		self.ban_timestamp = ban_timestamp
		self.target_user = target_user
		self.member_record = member_record
		self.disabled_role = disabled_role
		self.guild_id = guild_id
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
	async def cancel(self, interaction: Interaction, button: Button):
		button.disabled = True
		embed = Embed(
			description = f"This member has been released regardless of the Federation-wide regarding:\n```diff\n- {self.reason}```\nBanned at: <t:{self.ban_timestamp}:d> (<t:{self.ban_timestamp}:T>)"
		).set_footer(
			text = "Uwitz Federation",
			icon_url = self.bot_object.user.display_avatar.url
		)
		await self.target_user.remove_roles(self.disabled_role, reason = f"Released by {interaction.user.name}")
		await interaction.response.edit_message(embed = embed, view = self)

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
			disabled_role = self.bot.get_guild(member.guild.id).get_role(guild_config.get("roles").get("disabled"))
			await member.add_roles(disabled_role)
			report_channel = self.bot.get_channel(guild_config.get("moderation").get("request_channel"))
			report_embed = Embed(
				description = f"This member has been banned Federation-wide for:\n```diff\n- {member_record.get('infractions').get('global_ban').get('reason')}```\nBanned at: <t:{member_record.get('infractions').get('global_ban').get('timestamp')}:d> (<t:{member_record.get('global_ban').get('timestamp')}:T>)",
				colour = 0x2B2D31
			).set_author(
				name = "Banned user joined",
				icon_url = "https://cdn-icons-png.flaticon.com/512/4201/4201973.png"
			).set_footer(
				text = f"Uwitz Federation",
				icon_url = self.bot.user.display_avatar.url
			)
			return await report_channel.send(
				embed = report_embed,
				view = WarningPrompt(
					ban_timestamp = member_record.get("infractions").get("global_ban").get("reason"),
					target_user = member,
					record = member_record,
					disabled_role = disabled_role,
					guild_id = member.guild.id,
					reason = member_record.get("infractions").get("global_ban").get("reason")
				)
			)

async def setup(bot: Bot):
	await bot.add_cog(GlobalModeration(bot))