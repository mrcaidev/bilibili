import scrapy
import json
from bilibili.items import BilibiliItem
import re


class MainSpider(scrapy.Spider):
    name = 'main'

    def __init__(self):
        super().__init__()
        # Input AV/BV identifier.
        id = input('>>> 请输入AV/BV号: ')
        # Set urls.
        if id.startswith(('b', 'B')):
            self.start_urls = [
                f'https://api.bilibili.com/x/player/pagelist?bvid={id}&jsonp=jsonp']
            self.url = f'https://www.bilibili.com/video/{id}?p=%d'
        elif id.startswith(('a', 'A')):
            self.url = f'https://www.bilibili.com/video/{id}?p=%d'
            id = re.sub('av', '', id, flags=re.I)
            self.start_urls = [
                f'https://api.bilibili.com/x/player/pagelist?aid={id}&jsonp=jsonp']
        else:
            self.start_urls = [
                f'https://api.bilibili.com/x/player/pagelist?aid={id}&jsonp=jsonp']
            self.url = f'https://www.bilibili.com/video/av{id}?p=%d'

    def parse(self, response):
        # Get overall preview of the video.
        parts_list = json.loads(response.text)['data']

        # For each part of the video:
        for part in parts_list:
            # Get name and serial number.
            item = BilibiliItem()
            item['name'] = part['part']
            item['page'] = part['page']

            # Parse the url of current part.
            part_url = self.url % item['page']
            yield scrapy.Request(url=part_url, callback=self.parse_part, meta={'item': item})

    def parse_part(self, response):
        item = response.meta['item']
        # Parse the whole page.
        part_text = response.text

        # Extract the original url of video and audio.
        info_json = re.search(
            r'<script>window.__playinfo__=(.*?)</script>', part_text).group(1)
        info_json = json.loads(info_json)

        video_url = info_json['data']['dash']['video'][0]['backupUrl'][0]
        item['video_url'] = video_url

        audio_url = info_json['data']['dash']['audio'][0]['backupUrl'][0]
        item['audio_url'] = audio_url

        yield item
