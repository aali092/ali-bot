import io
import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from PIL import Image, ImageDraw

# تحميل التوكن من ملف .env السري
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# دالة دمج الصورة داخل قالب فخم وإطار احترافي
def apply_luxury_template(image_bytes: bytes) -> io.BytesIO:
  original = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
  img_w, img_h = original.size

  padding = 60
  canvas_w = img_w + (padding * 2)
  canvas_h = img_h + (padding * 2)

  canvas = Image.new("RGBA", (canvas_w, canvas_h), (15, 18, 24, 255))
  draw = ImageDraw.Draw(canvas)

  # إطار خارجي منحني فخم
  draw.rounded_rectangle(
      [10, 10, canvas_w - 10, canvas_h - 10],
      radius=25,
      outline=(35, 42, 54),
      width=2,
  )

  canvas.paste(original, (padding, padding), original)

  # إطار داخلي مزدوج ناعم حول الصورة
  border_box = [
      padding - 6,
      padding - 6,
      padding + img_w + 5,
      padding + img_h + 5,
  ]
  draw.rounded_rectangle(
      border_box, radius=12, outline=(160, 180, 200, 220), width=3
  )

  output = io.BytesIO()
  canvas.convert("RGB").save(output, format="PNG")
  output.seek(0)
  return output


class ImageActionView(View):

  def __init__(self, raw_image_bytes: bytes, filename: str):
    super().__init__(timeout=None)
    self.raw_image_bytes = raw_image_bytes
    self.filename = filename

  # زر التحميل - أيقونة فقط بدون كلام
  @discord.ui.button(emoji="📥", style=discord.ButtonStyle.primary)
  async def download_button(
      self, interaction: discord.Interaction, button: Button
  ):
    await interaction.response.defer(ephemeral=True)

    try:
      file = discord.File(
          io.BytesIO(self.raw_image_bytes), filename=self.filename
      )
      await interaction.user.send(file=file)
      await interaction.followup.send(
          "✅ تم إرسال الصورة الأصلية إلى خاصك بنجاح!", ephemeral=True
      )

    except discord.Forbidden:
      await interaction.followup.send(
          "❌ عذراً يا أبو حسين، رسائلك الخاصة (DMs) مغلقة!", ephemeral=True
      )
    except Exception:
      await interaction.followup.send(
          "❌ حدث خطأ أثناء إرسال الصورة.", ephemeral=True
      )

  # زر الحذف - أيقونة فقط بدون كلام (للإدارة فقط)
  @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
  async def delete_button(
      self, interaction: discord.Interaction, button: Button
  ):
    if not (
        interaction.user.guild_permissions.administrator
        or interaction.user.guild_permissions.manage_messages
    ):
      await interaction.response.send_message(
          "❌ عذراً، زر الحذف مخصص للإدارة العليا فقط يا بطل!", ephemeral=True
      )
      return

    await interaction.response.defer()
    try:
      await interaction.message.delete()
    except Exception:
      pass


@bot.command(name="صوره")
async def post_image(ctx):
  if not ctx.message.attachments:
    await ctx.send(
        "يرجى إرفاق صورة مع الأمر `!صوره` يا أبو حسين!", delete_after=10
    )
    try:
      await ctx.message.delete()
    except:
      pass
    return

  attachment = ctx.message.attachments[0]
  raw_bytes = await attachment.read()

  framed_image_io = apply_luxury_template(raw_bytes)
  framed_file = discord.File(framed_image_io, filename="framed_image.png")

  embed = discord.Embed(color=discord.Color.from_rgb(20, 24, 30))
  embed.set_image(url="attachment://framed_image.png")

  view = ImageActionView(raw_bytes, attachment.filename)
  await ctx.send(file=framed_file, embed=embed, view=view)

  try:
    await ctx.message.delete()
  except discord.Forbidden:
    pass


@bot.event
async def on_ready():
  print(f"البوت اشتغل بنجاح باسم: {bot.user}")


# تشغيل البوت بأمان تام عبر المتغير السري
bot.run(TOKEN)