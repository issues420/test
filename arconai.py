import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import http
from streamlink.plugin.api import useragents
from streamlink.stream import HLSStream
from streamlink.utils.unpacker import detect
from streamlink.utils.unpacker import unpack
from bs4 import BeautifulSoup
from streamlink.utils.aadecode import aadecode
import jsbeautifier.unpackers.packer as packer


class ArconaiTv(Plugin):
       _eval_re = re.compile(r'''(eval\s*\(function.*?)</script>''', re.DOTALL)
       _playlist_re = re.compile(r'''["'](?P<url>[^"']+.m3u8(?:[^"']+)?)["']''')
       _url_re = re.compile(r'''https?://(www\.)?(?:arconaitv\.us|arconai\.tv)/stream\.php\?id=\d+''')

       @classmethod
       def can_handle_url(cls, url):
        	return cls._url_re.match(url)

def _get_streams(self):
       headers = {
              'User-Agent': useragents.CHROME,
              'Referer': self.url
       }

       r = requests.get(url)
       html_text = r.text
       soup = BeautifulSoup(html_text, 'html.parser')
       scripts = soup.find_all('script')
       for script in scripts:
        	if script.string is not None:
			if "document.getElementsByTagName('video')[0].volume = 1.0;" in script.string: 
				code = script.string
			# Here is the call to the first part of the deobfuscation i.e. getting packed code
			code = aadecode(code)
			code = code.aadecode()
			if not code.replace(' ', '').startswith('eval(function(p,a,c,k,e,'):
				code = 'fail'
				break
			else:
				code = 'fail'
		else:
			code = 'fail'
	#The second part of deobfuscation occurs here. Using module jsbeautifier.
       if code != 'fail':
              unpacked = packer.unpack(code)
              video_location = unpacked[unpacked.rfind('http'):unpacked.rfind('m3u8')+4]
              url = video_location
              if url:
                     self.logger.debug('HLS URL: {0}'.format(url))
                     yield 'live', HLSStream(self.session, url, headers=headers)

__plugin__ = ArconaiTv
