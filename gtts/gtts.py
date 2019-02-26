from redbot.core import commands
from gtts import gTTS
from urllib.parse import quote
import os
from redbot.core.data_manager import cog_data_path
import tempfile
import pathlib
import asyncio
from redbot.cogs.audio import Audio
import logging

log = logging.getLogger("red.audio")

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        with tempfile.NamedTemporaryFile(dir=str(audiopath / 'localtracks') + '/', suffix = '.mp3') as tmpfile:
            print('Created file ' + tmpfile.name)
            playfp = pathlib.Path(tmpfile.name).relative_to(audiopath)
            print("Play Filepath: " + str(playfp))
            tts.write_to_fp(tmpfile)
            await ctx.invoke(Audio.play, query = 'localtracks:{}'.format(str(playfp)))
