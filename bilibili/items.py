# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BilibiliItem(scrapy.Item):
    # Name of the part.
    name = scrapy.Field()
    # Serial number of the part.
    page = scrapy.Field()
    # Audio url.
    audio_url = scrapy.Field()
    # Video url.
    video_url = scrapy.Field()
