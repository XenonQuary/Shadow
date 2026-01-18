import os
import discord
from discord.ext import commands
from collections import defaultdict, deque
import time

# -------------------- BOT SETUP --------------------
intents = discord.Intents.default()
intents.message_content = True  # Privileged Intent
intents.members = True          # Privileged Intent
bot = commands.Bot(command_prefix="/", intents=intents)

# -------------------- FEATURES --------------------
features = {
    "antiinvite": True,
    "antimention": True,
    "antiapp": True,
    "antispam": True,
}

# -------------------- ANTISPAM SETUP --------------------
user_messages = defaultdict(lambda: deque(maxlen=5))  # 5回まで履歴保持

# -------------------- EVENT HANDLER --------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    now = time.time()

    # -------------------- ANTIINVITE --------------------
    if features.get("antiinvite") and "discord.gg/" in message.content.lower():
        try:
            await message.delete()
            await message.author.send("⚠️ 招待リンクは禁止です！")
        except:
            pass

    # -------------------- ANTIMENTION --------------------
    if features.get("antimention") and "@everyone" in message.content.lower():
        try:
            await message.delete()
            await message.author.send("⚠️ @everyone の連続メンションは禁止です！")
        except:
            pass

    # -------------------- ANTIAPP --------------------
    if features.get("antiapp") and "<@&" in message.content:
        try:
            await message.delete()
            await message.author.send("⚠️ 外部アプリの利用は禁止です！")
        except:
            pass

    # -------------------- ANTISPAM --------------------
    if features.get("antispam"):
        user_messages[message.author.id].append((message.content, now))
        msgs = list(user_messages[message.author.id])
        if sum(1 for m, t in msgs if m == message.content and now - t < 10) >= 5:
            try:
                await message.delete()
                await message.author.send("⚠️ 短時間の同じメッセージ連投は禁止です！")
            except:
                pass
            user_messages[message.author.id].clear()

    await bot.process_commands(message)

# -------------------- COMMANDS --------------------
@bot.tree.command(name="say", description="BOTにメッセージを喋らせます")
async def say(interaction: discord.Interaction, *, content: str):
    await interaction.response.send_message(content)

@bot.tree.command(name="clear", description="チャンネルのメッセージを削除します")
async def clear(interaction: discord.Interaction, number: int):
    deleted = await interaction.channel.purge(limit=number)
    await interaction.response.send_message(f"🗑️ {len(deleted)} 件削除しました", ephemeral=True)

@bot.tree.command(name="nuke", description="チャンネルを完全リセット")
async def nuke(interaction: discord.Interaction):
    channel = interaction.channel
    new_channel = await channel.clone()
    await channel.delete()
    await new_channel.send("💣 チャンネルをリセットしました")

@bot.tree.command(name="slowmode", description="チャンネル低速モード設定")
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏱️ 低速モードを {seconds} 秒に設定しました", ephemeral=True)

@bot.tree.command(name="setup", description="荒らし対策機能を一括ONにします")
async def setup(interaction: discord.Interaction):
    for key in features.keys():
        features[key] = True
    await interaction.response.send_message("🛡️ すべての荒らし対策機能をONにしました", ephemeral=True)

@bot.tree.command(name="enable", description="個別機能をONにします")
async def enable(interaction: discord.Interaction, feature: str):
    if feature in features:
        features[feature] = True
        await interaction.response.send_message(f"✅ {feature} を有効化しました", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ {feature} は存在しません", ephemeral=True)

@bot.tree.command(name="disable", description="個別機能をOFFにします")
async def disable(interaction: discord.Interaction, feature: str):
    if feature in features:
        features[feature] = False
        await interaction.response.send_message(f"❌ {feature} を無効化しました", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ {feature} は存在しません", ephemeral=True)

@bot.tree.command(name="help", description="コマンド一覧を表示します")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Shadow コマンド一覧",
        description="🌑 管理・荒らし対策BOT",
        color=discord.Color.dark_purple()
    )
    embed.add_field(name="/say", value="BOTにメッセージを喋らせます", inline=False)
    embed.add_field(name="/clear [数]", value="チャンネルのメッセージを一括削除", inline=False)
    embed.add_field(name="/nuke", value="チャンネルを完全リセット", inline=False)
    embed.add_field(name="/setup", value="荒らし対策を一括ON", inline=False)
    embed.add_field(name="/enable", value="個別機能をON（antiinvite, antispam, antimention, antiapp）", inline=False)
    embed.add_field(name="/disable", value="個別機能をOFF", inline=False)
    embed.add_field(name="/slowmode [秒]", value="チャンネル低速モード設定", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -------------------- RUN BOT --------------------
bot.run(os.getenv("DISCORD_TOKEN"))
