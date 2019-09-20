# -*- coding: utf-8 -*-
import scrapy


class ScrapyXpathSpider(scrapy.Spider):
    name = 'scrapy_xpath'
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        divs = response.xpath('//div[@class="col-md-8"]/div')
        for div in divs:
            text = div.xpath('./span[@class="text"]/text()').get()
            author = div.xpath('./span/small/text()').get()
            tags = div.xpath('./div/a/text()').getall()
            item = {
                'text': text,
                'author': author,
                'tags': tags
            }
            yield item
        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page)