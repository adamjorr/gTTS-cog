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

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        print('Query:',query)
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        with tempfile.NamedTemporaryFile(dir = str(audiopath / 'localtracks') + '/', suffix = '.mp3') as file
            filepath = file.name
            print(f'Opened path {filepath}')
            tts = gTTS(query, lang)
            tts.write_to_fp(file)
            print(f'File {filepath} should be written to.')
            playfp = pathlib.Path(filepath).relative_to(audiopath)
            q = 'localtrack:{}'.format(str(playfp))
            print(f'Playfp is {playfp}')
            try:
                await asyncio.wait_for(ctx.invoke(Audio.play, query = q), timeout = 60)
            except asyncio.TimeoutError:
                await Audio._embed_msg(ctx, 'Playing file took too long.') #TODO: don't use private methods
            duration = await Audio._queue_duration(ctx) #TODO: don't use private methods
            await asyncio.sleep(duration + 1) #TODO: actually use a callback to tell when the track is done
        print(f'Removing {filepath}')
