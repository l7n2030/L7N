import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from keep_alive import keep_alive

# إعدادات البوت والصلاحيات
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# تحديد مسار ملف الكوكيز تلقائياً
cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')

# إعدادات yt-dlp الشاملة لدعم كل المنصات وتجاوز القيود
ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',  # يدعم البحث النصي المباشر أو الروابط لكل المنصات
    'source_address': '0.0.0.0',
    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'مقطع صوتي')
        self.url = data.get('url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        # استخراج البيانات من أي منصة تدعمها yt-dlp تلقائياً
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user.name}')

# أمر استدعاء البوت للقناة الصوتية
@bot.command(name="come")
async def come_channel(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send("حياك الله، تم الدخول للقناة الصوتية! 🎙")
    else:
        await ctx.send("يا أبو محمد، لازم تكون داخل قناة صوتية أولاً!")

# أمر تشغيل الصوت الشامل (يوتيوب، ساوند كلاود، وكل المنصات)
@bot.command(name="ش")
async def play_audio(ctx, *, query):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("يا أبو محمد، لازم تدخل قناة صوتية أولاً!")
            return

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'خطأ في التشغيل: {e}') if e else None)
            await ctx.send(f"جار الآن تشغيل من المنصة المدعومة: **{player.title}** 🎶")
        except Exception as e:
            await ctx.send(f"صار خطأ أثناء جلب الرابط أو التشغيل: {e}")

# أمر الإيقاف المؤقت
@bot.command(name="وقف")
async def pause_audio(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("تم إيقاف التشغيل مؤقتاً ⏸")
    else:
        await ctx.send("مافي شي شغال حالياً عشان أوقفه.")

# أمر الاستئناف
@bot.command(name="كمل")
async def resume_audio(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("تم استئناف التشغيل ▶️")
    else:
        await ctx.send("البوت ليس في حالة إيقاف مؤقت.")

# أمر إخراج البوت من القناة
@bot.command(name="خ")
async def leave_channel(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("تم الخروج من القناة الصوتية 👋")
    else:
        await ctx.send("البوت أساساً مو في أي قناة صوتية.")

if __name__ == "__main__":
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("خطأ: لم يتم العثور على التوكن في متغيرات البيئة!")
    else:
        bot.run(token)
