import os
import re

from datetime import datetime, timedelta

from discord import Button, ButtonStyle, Embed, Interaction, Member, TextChannel
from discord.ui import View, button
from discord.app_commands import command, describe
from discord.ext.commands import Cog

class BanPrompt(View):
	def __init__(self, target_user: Member, reason: str, original_embed: Embed):
		self.target_user = target_user
		self.reason = reason
		self.original_embed = original_embed
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
			return await interaction.response.send_message(f"{os.getenv("EMOJI_FAIL")} The Royal Defence is not authorised to ban this user.")
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
		label = "Cancel",
		style = ButtonStyle.grey
	)
	async def cancel(self, button: Button, interaction: Interaction):
		button.disabled = True
		for button_ in self.children:
			button.disabled = True
			button_.style = ButtonStyle.grey

		button.style = ButtonStyle.green
		await self.target_user.timeout(until = None)
		await interaction.edit_original_response(
			embed = self.original_embed.add_field(
				name = "Cancelled by:",
				value = f"<@!{interaction.user.id}>"
			),
			view = self
		)

class Prompt(View):
	def __init__(self, target_user: Member, report_channel: TextChannel, reason: str):
		self.target_user = target_user
		self.report_channel = report_channel
		self.original_reason = reason
		super().__init__(timeout = None)

	@button(
		label = "Confirm",
		style = ButtonStyle.red
	)
	async def confirm(self, button: Button, interaction: Interaction):
		duration = timedelta(days = 5)
		await self.target_user.timeout(duration, reason = "Waiting for banishment requestion completion.")
		embed = Embed(
			description = f"Report sent to enforcement regarding <@!{self.target_user.id}>:\n```diff\n- {self.original_reason}\n```",
			timestamp = datetime.now(),
			colour = 0xFF7A7A
		).set_author(
			name = self.target_user.display_name,
			icon_url = self.target_user.display_avatar.url
		)
		await interaction.response.edit_message(embed = embed)

		report_embed = Embed(
			description = f"Ban report by <@!{interaction.user.id}>\n\n**Reason:**\n```diff\n - {self.reason}\n```",
			timestamp = datetime.now(),
			colour = 0xFF7A7A
		).set_author(
			name = self.target_user.display_name,
			icon_url = self.target_user.display_avatar.url
		)

		await self.report_channel.send(
			embed = report_embed,
			view = BanPrompt(
				target_user = self.target_user,
				reason = self.reason,
				original_embed = report_embed
			)
		)


	@button(
		label = "Cancel",
		style = ButtonStyle.grey
	)
	async def cancel(self, button, interaction):
		await interaction.response.edit_message(
			content = f"{os.getenv("EMOJI_SUCCESS")} Cancelled Ban Request"
		)

class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(
		name = "ban",
		description = "Banish a member with a valid reason.",
	)
	@describe(member = "The member you'd like banished.")
	@describe(reason = "Why should the member be banned?")
	async def ban(self, interaction: Interaction, member: Member, reason: str):
		report_channel = self.bot.get_channel(os.getenv("ENFORCEMENT"))
		if not interaction.user.id == int(os.getenv("OWNER_ID")):
			if (interaction.guild.get_role(os.getenv("ADMINISTRATOR_ROLE")) in interaction.user.roles) or (interaction.user.guild_permissions.administrator):
				if interaction.user.guild_permissions.administrator or (
					(os.getenv("ADMINISTRATOR_ROLE"), os.getenv("MODERATOR_ROLE")) in [role.id for role in interaction.user.roles]
				):
					await interaction.response.send(f"{os.getenv("EMOJI_FAIL")} You are not authorised to moderate another person in authority.")
				report = Embed(
					description = f"Sudo Banned by <@!{interaction.user.id}>\n\n**Reason:**\n```diff\n - {reason}```",
					timestamp = datetime.now(),
					color = 0xFF7A7A
				).set_author(
					name = member.display_name,
					icon_url = member.display_avatar.url
				)

				try:
					await member.ban(
						reason = reason,
						delete_message_seconds = 60
					)
				except:
					return await interaction.response.send_message(f"{os.getenv("EMOJI_FAIL")} The Royal Defence is not authorised to ban this user.")

				await report_channel.send(embed = report)
				return await interaction.response.send_message(f"{os.getenv("EMOJI_SUCCESS")} Successfully Sudo Banished User.", ephemeral = True)

			confirmation_embed = Embed(
				description = f"Would you like to confirm that you want to send a ban report about <@!{member.id}> for:\n```diff\n- {reason}\n```",
				timestamp = datetime.now(),
				colour = 0xFF7A7A
			).set_author(
				name = member.display_name,
				icon_url = member.display_avatar.url
			)

			await interaction.response.send_message(
				embed = confirmation_embed,
				view = Prompt(
					target_user = member,
					reason = reason,
					report_channel = report_channel
				)
			)

		else:
			report = Embed(
				description = f"Sudo Banned by <@!{interaction.user.id}>\n\n**Reason:**\n```diff\n - {reason}```",
				timestamp = datetime.now(),
				color = 0xFF7A7A
			).set_author(
				name = member.display_name,
				icon_url = member.display_avatar.url
			)

			try:
				await member.ban(
					reason = reason,
					delete_message_seconds = 60
				)
			except:
				return await interaction.response.send_message(f"{os.getenv("EMOJI_FAIL")} The Royal Defence is not authorised to ban this user.", ephemeral = True)

			await report_channel.send(embed = report)
			return await interaction.response.send_message(f"{os.getenv("EMOJI_SUCCESS")} Successfully Sudo Banished User.", ephemeral = True)

	@command(
		name = "mute",
		description = "Mute a member with a valid reason."
	)
	async def mute(self, interaction: Interaction, member: Member, duration: str, reason: str):
		if re.compile(r"^[0-9]+[hdmy]$", re.IGNORECASE).match(duration) is None:
			return await interaction.response.send_message(f"{os.getenv("EMOJI_FAIL")} Invalid duration format. Please use the following format: `1h`, `2d`, `3m` or `4y`.", ephemeral = True)

		duration_unit = duration[-1].lower()
		if duration_unit == 'h':
			future_time = timedelta(hours = int(duration[:-1]))
		elif duration_unit == 'd':
			future_time = timedelta(days = int(duration[:-1]))
		elif duration_unit == 'm':
			future_time = timedelta(minutes = int(duration[:-1]))
		elif duration_unit == 'y':
			future_time = timedelta(years = int(duration[:-1]))
		else:
			return await interaction.response.send_message(f"{os.getenv("EMOJI_FAIL")} Invalid duration unit. Please use one of the following units: `h`, `d`, `m`, `y`.", ephemeral=True)

		if not interaction.user.id == int(os.getenv("OWNER_ID")):
			if (interaction.guild.get_role(os.getenv("ADMINISTRATOR_ROLE")) in interaction.user.roles) or (interaction.user.guild_permissions.administrator):
				if interaction.user.guild_permissions.administrator or (
					(os.getenv("ADMINISTRATOR_ROLE"), os.getenv("MODERATOR_ROLE")) in [role.id for role in interaction.user.roles]
				):
					await interaction.response.send(f"{os.getenv("EMOJI_FAIL")} You are not authorised to moderate another person in authority.")
				return

		await member.timeout(until = future_time, reason = reason)
		await interaction.response.send_message(f"{os.getenv("EMOJI_SUCCESS")} Successfully Muted User.", ephemeral = True)

async def setup(bot):
	await bot.add_cog(Mod(bot))