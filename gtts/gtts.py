from redbot.core import commands
import lavalink
from gtts import gTTS
from io import BytesIO
import codecs
from urllib.parse import quote

class Gtts(commands.Cog):
    """Speak using gTTS."""

    @commands.command()
    async def say(self, ctx, *, query, lang = 'en'):
        """Have the bot say something."""
        bytefp = BytesIO()
        tts = gTTS(query, lang)
        tts.write_to_fp(bytefp)
        bytestr = codecs.encode(bytefp.getvalue(), encoding = 'base64').decode()
        bytestr = bytestr.replace('+','-')
        bytestr = bytestr.replace('\\','_')
        player = lavalink.get_player(ctx.guild.id)
        req_url = "http://{}:{}/decodetrack?track={}".format(
            player._node.host, player._node.rest, quote(bytestr))
        async with player._session.get(req_url, headers = player._headers) as resp:
            data = await resp.json(content_type=None)
        try:
            track = data["tracks"] if type(data) is dict else data
        except KeyError:
            print("request:")
            print(req_url)
            print("data:")
            print(data)
            raise
        track = Track(track[0])
        player.add(ctx.author, track)
        if not player.current:
            player.play
