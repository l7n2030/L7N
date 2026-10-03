import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# --- أوامر الموسيقى والتحكم ---

@bot.command(name="ش")
async def play_short(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("!يجب أن تكون في قناة صوتية أولاً")
            return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'خطأ في التشغيل: {e}') if e else None)
            await ctx.send(f"جار الآن تشغيل **{player.title}**")
        except Exception as e:
            await ctx.send(f"صار خطأ أثناء البحث أو التشغيل: {e}")

@bot.command(name="وقف")
async def pause_audio(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("تم إيقاف الأغنية مؤقتاً ⏸")
    else:
        await ctx.send("مافي شي شغال حالياً عشان أوقفه")

@bot.command(name="خ")
async def leave_short(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("تم الخروج من القناة الصوتية")
    else:
        await ctx.send("البوت ليس في أي قناة صوتية")

# تشغيل البوت بأمان عبر متغير البيئة
bot.run(os.getenv("DISCORD_TOKEN"))