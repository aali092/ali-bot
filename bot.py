import discord
from discord.ext import commands
from discord.ui import Button, View
import io

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class DownloadView(View):
    def __init__(self, image_attachment: discord.Attachment):
        super().__init__(timeout=None)
        self.image_attachment = image_attachment
        
    @discord.ui.button(label="تحميل 4K", emoji="📥", style=discord.ButtonStyle.primary)
    async def download_4k(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.send_message("جاري إرسال الصورة الأصلية (4K) إلى رسائلك الخاصة... 🚀", ephemeral=True)
            
            image_bytes = await self.image_attachment.read()
            file = discord.File(io.BytesIO(image_bytes), filename=self.image_attachment.filename)
            
            await interaction.user.send(
                content="هاك يا بطل، صورتك الأصلية بدقة عالية:",
                file=file
            )
            
            await interaction.edit_original_response(content="✅ تم إرسال الصورة إلى رسائلك الخاصة بنجاح!")
            
        except discord.Forbidden:
            await interaction.edit_original_response(content="❌ عذراً، رسائلك الخاصة مغلقة! يرجى فتح الخاص ليتسنى للبوت إرسال الصورة.")
        except Exception as e:
            print(f"خطأ: {e}")
            await interaction.edit_original_response(content="❌ حدث خطأ أثناء إرسال الصورة، جرب مرة أخرى.")

@bot.command(name="صوره")
async def post_image(ctx, *, title: str = "خلفية مميزة"):
    if not ctx.message.attachments:
        await ctx.send("يرجى إرفاق صورة مع الأمر `!صوره` (اسحب الصورة أو ارفعها مع كتابة الأمر)، يا بطل!", delete_after=10)
        try:
            await ctx.message.delete()
        except:
            pass
        return

    attachment = ctx.message.attachments[0]
    
    embed = discord.Embed(
        title=title,
        description="اضغط على زر **تحميل 4K** أدناه ليقوم البوت بإرسال الصورة الأصلية مباشرة إلى رسائلك الخاصة.",
        color=discord.Color.blue()
    )
    embed.set_image(url=attachment.url)
    embed.set_footer(text=f"بواسطة: {ctx.author.name}")
    
    view = DownloadView(attachment)
    sent_message = await ctx.send(embed=embed, view=view)
    
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

@bot.event
async def on_ready():
    print(f"البوت اشتغل بنجاح باسم: {bot.user}")

bot.run("MTU0NnZE4TKzOTI3OKxMzMzA5Mg..GpsUQV.5TjveyFDdvj8YZef99l3NZW4Mu9CalooM1MC")
