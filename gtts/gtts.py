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
import aiofiles

log = logging.getLogger("red.audio")

async def query_and_write(query, lang, flo):
    tts = gTTS(query, lang)
    tts.write_to_fp(flo)

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        print('Query:',query)
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        file = tempfile.NamedTemporaryFile(dir = str(audiopath / 'localtracks') + '/', suffix = '.mp3', delete = False)
        filepath = file.name
        file.close()
        print(f'Opened and closed path {filepath}')
        async with aiofiles.open(filepath, mode = 'wb') as tmpfile:
            print(f'Reopened path {filepath}')
            try:
                await asyncio.wait_for(query_and_write(query, lang, tmpfile), timeout = 60)
                print(f'File {filepath} should be written to.')
            except asyncio.TimeoutError:
                await Audio._embed_msg(ctx, 'Request timed out.')
        playfp = pathlib.Path(filepath).relative_to(audiopath)
        q = 'localtrack:{}'.format(str(playfp))
        print(f'Playfp is {playfp}')
        try:
            await asyncio.wait_for(ctx.invoke(Audio.play, query = q), timeout = 60)
            print(f'Waited for file {playfp}')
        except asyncio.TimeoutError:
            await Audio._embed_msg(ctx, 'Playing file took too long.')
        os.remove(filepath)
        print(f'Removing {filepath}')
