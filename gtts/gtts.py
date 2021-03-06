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
    log.debug(f"Handling an event: {event} with extra {extra}")
    if event == lavalink.LavalinkEvents.TRACK_END:
        if extra == lavalink.TrackEndReason.FINISHED or \
        extra == lavalink.TrackEndReason.CLEANUP or \
        extra == lavalink.TrackEndReason.REPLACED or \
        extra == lavalink.TrackEndReason.STOPPED:
            #the track needs to be deleted
            log.debug(f"We need to delete a track")
            queue = [t.uri for t in player.queue]
            log.debug(f"Current queue is {queue}")
            removed = []
            tmpfiles = player.fetch('gtts-tmp-files',[])
            log.debug(f"Temp files are {tmpfiles}")
            for tmpfile in tmpfiles:
                if tmpfile not in queue:
                    rmpath = cog_data_path(raw_name='Audio')/tmpfile
                    os.remove(rmpath)
                    log.info(f"Deleted {rmpath}")
                    removed.append(tmpfile)
            for tmpfile in removed:
                tmpfiles.remove(tmpfile)
            if len(tmpfiles) == 0:
                lavalink.unregister_event_listener(wait_for_end)
                log.debug("Unregistering myself")
        elif extra is lavalink.TrackEndReason.LOAD_FAILED:
            #the track didn't load. should we try again?
            log.info("a track failed to load.")

async def send_embed(ctx, title):
    embed = discord.Embed(colour=await ctx.embed_colour(), title = title)
    await ctx.send(embed = embed)

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        log.debug(f'Query: {query}')
        tts = gTTS(query, lang)
        audiopath = cog_data_path(raw_name='Audio')
        tmppath = audiopath / 'localtracks/gtts-tmp/'
        os.makedirs(tmppath, exist_ok=True)
        file = tempfile.NamedTemporaryFile(dir = tmppath, suffix = '.mp3', delete = False)
        filepath = file.name
        log.debug(f'Opened path {filepath}')
        tts = await query_gtts(query, lang)
        await write_gtts(tts,file)
        file.close()
        log.info(f'Wrote to {filepath}.')
        playfp = pathlib.Path(filepath).relative_to(audiopath)
        q = 'localtrack:{}'.format(str(playfp))
        log.debug(f'Playfp is {playfp}')
        await ctx.invoke(Audio.play, query = q)
        player = lavalink.get_player(ctx.guild.id)
        gtts_tmp_files = player.fetch('gtts-tmp-files',[])
        gtts_tmp_files.append(playfp)
        player.store('gtts-tmp-files', gtts_tmp_files)
        log.debug(f"Stored tmp files with player: {gtts_tmp_files}")
        lavalink.register_event_listener(wait_for_end)
        log.debug("Attached wait_for_end listener")
