from discord import ButtonStyle, Embed, Interaction
from discord.ui import View, Button
from discord.app_commands import command
from discord.ext.commands import Bot, Cog

class Copyright(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.project_url_location = "Uwitz/Disect"

    @command(
        name = "copyright",
        description = "View internal code copyright."
    )
    async def copyright(self, interaction: Interaction):
        embed = Embed(
            description = "This software has been programmed and licenced under the [Uwitz Federation](https://uwitz.org/discord) with an GNU Affero General Public License version 3.",
            colour = 0x2B2D31
        ).set_author(
            name = "Copyright Notice",
            icon_url = "http://cdn.uwitz.org/r/justice.png"
        ).set_footer(
            text = "Uwitz Federation",
            icon_url = "http://cdn.uwitz.org/r/shield-logo.png"
        )
        await interaction.response.send_message(
            embed = embed,
            view = View().add_item(
                Button(
                    label = "Github",
                    style = ButtonStyle.link,
                    url = f"https://github.com/{self.bot.project_url_location}"
                )
            ).add_item(
                Button(
                    label = "View Licence",
                    style = ButtonStyle.link,
                    url = f"https://raw.githubusercontent.com/{self.bot.project_url_location}/master/LICENSE"
                )
            )
        )

async def setup(bot: Bot):
    await bot.add_cog(Copyright(bot))