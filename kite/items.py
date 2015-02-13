# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class KiteItem(Item):
    # define the fields for your item here like:
    # name = scrapy.scrapy.Field()
    link = Field()
    model = Field()
    riding_type = Field()
    year = Field()
    brand = Field()
    size = Field()
    type = Field()
    one_pump = Field()
    bridles = Field()
    num_of_struts = Field()
    colors = Field()
    line_length = Field()
    bar_length = Field()
    bar = Field()
    depower = Field()
    safety = Field()
    swivel = Field()
    variable_bar_length = Field()
    oh_shit_handles = Field()
