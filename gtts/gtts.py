from redbot.core import commands
from gtts import gTTS
from urllib.parse import quote
import os
from redbot.core.data_manager import cog_data_path
import tempfile
import pathlib
import asyncio

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        with tempfile.TemporaryDirectory(prefix=str(audiopath / 'localtracks') + '/') as tmpdir:
            pipefp = pathlib.Path(tmpdir) / 'gtts.mp3'
            os.mkfifo(pipefp)
            playfp = pipefp.relative_to(audiopath)
            ctx.bot.loop.gather(
                tts.save(pipefp)
                ctx.invoke(self.play, query = 'localtracks:{}'.format(str(playfp)))
            )
            #tts.save(pipefp)
            #await ctx.invoke(self.play, query = 'localtracks:{}'.format(str(playfp)))
