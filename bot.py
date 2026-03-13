import discord
from discord.ext import commands
import asyncio
from flask import Flask
from threading import Thread

# -------- anti sleep --------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

allowed_users = ["almani_14", "mstranmi"]
stop_sending = False


class ControlPanel(discord.ui.View):

    @discord.ui.button(label="📩 إرسال لشخص واحد", style=discord.ButtonStyle.green)
    async def send_one(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.name not in allowed_users:
            await interaction.response.send_message("❌ ليس لديك صلاحية", ephemeral=True)
            return

        await interaction.response.send_message("منشن الشخص ثم اكتب الرسالة", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.mentions

        msg = await bot.wait_for("message", check=check)

        member = msg.mentions[0]
        text = msg.content.replace(member.mention, "").strip()

        try:
            await member.send(text)
            await interaction.followup.send("✅ تم إرسال الرسالة", ephemeral=True)
        except:
            await interaction.followup.send("❌ لم أستطع إرسال الرسالة", ephemeral=True)


    @discord.ui.button(label="📨 إرسال لكل السيرفر", style=discord.ButtonStyle.red)
    async def send_all(self, interaction: discord.Interaction, button: discord.ui.Button):

        global stop_sending
        stop_sending = False

        if interaction.user.name not in allowed_users:
            await interaction.response.send_message("❌ ليس لديك صلاحية", ephemeral=True)
            return

        await interaction.response.send_message("اكتب الرسالة لإرسالها لكل الأعضاء", ephemeral=True)

        def check(m):
            return m.author == interaction.user

        msg = await bot.wait_for("message", check=check)

        sent = 0

        for member in interaction.guild.members:

            if stop_sending:
                break

            if member.bot:
                continue

            try:
                await member.send(msg.content)
                sent += 1
                await asyncio.sleep(2)
            except:
                pass

        await interaction.followup.send(f"📊 تم إرسال {sent} رسالة", ephemeral=True)


    @discord.ui.button(label="👥 إرسال لرتبة", style=discord.ButtonStyle.blurple)
    async def send_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.name not in allowed_users:
            await interaction.response.send_message("❌ ليس لديك صلاحية", ephemeral=True)
            return

        await interaction.response.send_message("منشن الرتبة ثم اكتب الرسالة", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.role_mentions

        msg = await bot.wait_for("message", check=check)

        role = msg.role_mentions[0]
        text = msg.content.replace(role.mention, "").strip()

        sent = 0

        for member in role.members:

            if member.bot:
                continue

            try:
                await member.send(text)
                sent += 1
                await asyncio.sleep(2)
            except:
                pass

        await interaction.followup.send(f"📊 تم إرسال الرسالة إلى {sent} عضو", ephemeral=True)


    @discord.ui.button(label="⛔ إيقاف الإرسال", style=discord.ButtonStyle.gray)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):

        global stop_sending
        stop_sending = True

        await interaction.response.send_message("🛑 تم إيقاف الإرسال", ephemeral=True)


@bot.command()
async def panel(ctx):

    if ctx.author.name not in allowed_users:
        await ctx.send("❌ ليس لديك صلاحية")
        return

    embed = discord.Embed(
        title="لوحة إرسال الرسائل",
        description="اختر العملية من الأزرار",
        color=0x00ff99
    )

    await ctx.send(embed=embed, view=ControlPanel())


# -------- إدارة المستخدمين --------
@bot.command()
async def adduser(ctx, user: str):

    if ctx.author.name not in allowed_users:
        await ctx.send("❌ ليس لديك صلاحية")
        return

    if user in allowed_users:
        await ctx.send("⚠️ المستخدم موجود")
    else:
        allowed_users.append(user)
        await ctx.send(f"✅ تم إضافة {user}")


@bot.command()
async def removeuser(ctx, user: str):

    if ctx.author.name not in allowed_users:
        await ctx.send("❌ ليس لديك صلاحية")
        return

    if user not in allowed_users:
        await ctx.send("⚠️ المستخدم غير موجود")
    else:
        allowed_users.remove(user)
        await ctx.send(f"🗑️ تم إزالة {user}")


# تشغيل anti sleep
keep_alive()

# تشغيل البوت
bot.run("YOUR_BOT_TOKEN")
import os
bot.run(os.getenv("TOKEN"))
