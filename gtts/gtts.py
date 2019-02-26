from redbot.core import commands
from gtts import gTTS
from urllib.parse import quote
import os
from redbot.core.data_manager import cog_data_path
import tempfile

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        async with tempfile.TemporaryDirectory(prefix=audiopath) as tmpdir:
            pipefp = pathlib.Path(tmpdir) / 'gtts.mp3'
            os.mkfifo(pipefp)
            tts.save(pipefp)
            playfp = pipefp.relative_to(audiopath)
            await ctx.invoke(self.play, query = 'localtracks:{}'.format(str(playfp)))
