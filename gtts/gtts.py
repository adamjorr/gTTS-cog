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
import lavalink

log = logging.getLogger("red.audio")

async def query_gtts(query, lang):
    return gTTS(query, lang)

async def write_gtts(gtts, file):
    return gtts.write_to_fp(file)

async def wait_for_end(player, event, extra):
    if event is lavalink.LavalinkEvents.TRACK_END:
        if extra is lavalink.TrackEndReason.FINISHED or \
        extra is lavalink.TrackEndReason.CLEANUP or \
        extra is lavalink.TrackEndReason.REPLACED:
            #the track needs to be deleted
            queue = [t.uri for t in player.queue]
            removed = []
            tmpfiles = player.fetch('gtts-tmp-files',[])
            for tmpfile in tmpfiles:
                if tmpfile not in queue:
                    os.remove(cog_data_path(raw_name='Audio') / tmpfile)
                    removed.append(tmpfile)
            for tmpfile in removed:
                tmpfiles.remove(tmpfile)
            if len(tmpfiles) == 0:
                lavalink.unregister_event_listener(wait_for_end)
        elif extra is lavalink.TrackEndReason.LOAD_FAILED:
            #the track didn't load. should we try again?
            print("a track failed to load.")

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        print('Query:',query)
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        file = tempfile.NamedTemporaryFile(dir = str(audiopath / 'localtracks/gtts-tmp') + '/', suffix = '.mp3', delete = False)
        filepath = file.name
        print(f'Opened path {filepath}')
        tts = await query_gtts(query, lang)
        await write_gtts(tts,file)
        file.close()
        print(f'File {filepath} should be written to.')
        playfp = pathlib.Path(filepath).relative_to(audiopath)
        q = 'localtrack:{}'.format(str(playfp))
        print(f'Playfp is {playfp}')
        await ctx.invoke(Audio.play, query = q)
        player = lavalink.get_player(ctx.guild.id)
        gtts_tmp_files = player.fetch('gtts-tmp-files',[])
        player.store('gtts-tmp-files', gtts_tmp_files.append(playfp))
        lavalink.register_event_listener(wait_for_end)
