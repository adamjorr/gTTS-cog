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
        with tempfile.NamedTemporaryFile(dir=str(audiopath / 'localtracks') + '/', suffix = '.mp3') as tmpfile:
            playfp = pathlib.Path(tmpfile.name).relative_to(audiopath)
            tts.write_to_fp(tmpfile)
            await ctx.invoke(self.play, query = 'localtracks:{}'.format(str(playfp)))
