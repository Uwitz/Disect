import os

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from discord import Embed, Interaction, SelectOption
from discord.ui import RoleSelect
from discord.app_commands import command
from discord.ext.commands import Cog

class AdminRoleSelect(RoleSelect):
    def __init__(self):
        super().__init__(placeholder = "Select your admin role(s)")

class ModRoleSelect(RoleSelect):
	def __init__(self):
		super().__init__(placeholder = "Select your mod role(s)")

	async def callback(interaction):
		if os.getenv("MONGO_TLS") == "True":
			collection = AsyncIOMotorClient(
				os.getenv("MONGO"),
				tls = True,
				tlsCertificateKeyFile = "mongo_cert.pem"
			)["Discord"]["server_conf"]
			if await collection.find_one(
				{
					"_id": interaction.guild.id
				}
			) is None:
				await collection.insert_one(
					{
						"_id": interaction.guild.id,
						"moderator_roles": interaction
					}
				)

class Setup(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(
		name = "setup",
		description = "Setup Disect for your Discord Server."
	)
	async def setup(self, interaction: Interaction):
		if interaction.guild is None:
			return await interaction.response.send_message(
				f"{os.getenv("EMOJI_FAIL")} Command unable to be invoked in DMs.",
				ephemeral = True
			)
		if not interaction.user.guild_permissions.administrator:
			return await interaction.response.send_message(
				f"{os.getenv("EMOJI_FAIL")} You are not authorised to invoke this command.",
				ephemeral = True
			)

		embed = Embed(
			colour = 0xF0C40F,
			description = "You can select your Moderator Roles for the bot. This way Moderators do not need kick or ban permissions on their role to kick and ban users through this bot. This increases the safety from rogue staff members banning or kicking many members.",
			timestamp = datetime.utcnow().isoformat()
		)
		embed.set_author(
			name = "Server Setup",
			icon_url = interaction.guild.icon.url
		)

async def setup(bot):
	await bot.add_cog(Setup(bot))