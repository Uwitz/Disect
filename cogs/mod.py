import os
import re

from datetime import datetime, timedelta

from discord import Embed, Forbidden, Interaction, Member, TextChannel
from discord.app_commands import command, describe
from discord.ext.commands import Cog

from cogs.utils.checks import Checks

class Mod(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(
		name = "ban",
		description = "Bans a member with a valid reason.",
	)
	@describe(member = "The member you'd like banned.")
	@describe(reason = "Why should the member be banned?")
	async def ban(self, interaction: Interaction, member: Member, reason: str):
		guild_config = await self.bot.database["config"].find_one(
			{
				"_id": interaction.guild.id
			}
		)
		if not guild_config:
			return await interaction.response.send_message(f"{self.bot.metadata.get('EMOJI_FAIL')} This server has not been configured yet. Please ask an administrator to run the `/setup` command.", ephemeral = True)
		
		report_channel: TextChannel = interaction.guild.get_channel(guild_config.get("channels").get("moderation_log"))
		roles = guild_config.get("roles").get("administrators").extend(guild_config.get("roles").get("moderators"))
		if ([role.id for role in member.roles] in roles) or (interaction.user.guild_permissions.administrator):
			await interaction.response.send(f"{self.bot.metadata.get("EMOJI_FAIL")} You are not authorised to moderate another person in authority.")
			report = Embed(
				description = f"Banned by <@!{interaction.user.id}>\n\n**Reason:**\n```diff\n - {reason}```",
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
			except Forbidden:
				return await interaction.response.send_message(f"{self.bot.metadata.get("EMOJI_FAIL")} I am not authorised to ban this user.")
			except Exception as error:
				return await interaction.response.send_message(f"{self.bot.metadata.get("EMOJI_FAIL")} Banning failed. (`{error.__class__.__name__}`)")

			await report_channel.send(embed = report)
			return await interaction.response.send_message(f"{self.bot.metadata.get("EMOJI_SUCCESS")} Successfully banned user.", ephemeral = True)

	@command(
		name = "mute",
		description = "Mute a member with a valid reason."
	)
	async def mute(self, interaction: Interaction, member: Member, duration: str, reason: str):
		server_config: dict | None = await self.bot.database["config"].find_one(
			{
				"_id": member.guild.id
			}
		)
		if re.compile(r"^[0-9]+[hdmy]$", re.IGNORECASE).match(duration) is None:
			return await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_FAIL')} Invalid duration format. Please use the following format: `1h`, `2d`, `3m` or `4y`.",
				ephemeral = True
			)

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
			return await interaction.response.send_message(
				f"{self.bot.metadata.get('EMOJI_FAIL')} Invalid duration unit. Please use one of the following units: `h`, `d`, `m`, `y`.",
				ephemeral = True
			)

		if not interaction.user.id == interaction.guild.owner.id:
			if (
					(
						(not Checks.roles_in_roles(server_config.get("roles").get("administrators"), interaction.user.roles)) or
						(not Checks.roles_in_roles(server_config.get("roles").get("moderators"), interaction.user.roles))
					) and not interaction.user.guild_permissions.administrator
				):
					return await interaction.response.send(f"{self.bot.metadata.get('EMOJI_FAIL')} You are not authorised to moderate another authoritative user.")

			else:
				await member.timeout(
					duration = future_time,
					reason = reason
				)
				return await interaction.response.send_message(f"{self.bot.metadata.get('EMOJI_SUCCESS')} Muted user successfully.")

async def setup(bot):
	await bot.add_cog(Mod(bot))