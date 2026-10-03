import os
import threading
import discord
from discord.ext import commands
import yt_dlp
import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return "L7N Bot is alive and running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command(name='play', help='يشغل الصوت من الرابط')
async def play(ctx, *, url):
    if not ctx.author.voice:
        await ctx.send("يا أبو محمد لازم تدخل روم صوتي أول! 🎙️")
        return

    channel = ctx.author.voice.channel
    
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info.get('url') or info['entries'][0]['url']
            
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
            
            await ctx.send(f'🎵 جاري تشغيل: **{info.get("title", "الصوت")}**')
        except Exception as e:
            await ctx.send(f'صار فيه خطأ أثناء تشغيل المقطع: `{e}`')

@bot.command(name='stop', help='يوقف البوت ويطلعه من الروم')
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('تم إيقاف الصوت والخروج من الروم بنجاح! 🛑')
    else:
        await ctx.send('البوت أصلاً ماهو في روم صوتي!')

if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.start()
    
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
