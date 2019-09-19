# -*- coding: utf-8 -*-

from easyspider.spiders.easyCrawlSpider import easyCrawlSpider
from scrapy import Request, FormRequest
from DBService import MysqlService
import json
import re
import urllib
import pdb
import os


class AccessData(easyCrawlSpider):

    name = "AccessDataSpider"

    custom_settings = {
        "ITEM_PIPELINES": {
            "easyspider.pipelines.commonBasepipeline.commonBasepipeline": 500,
            "easyspider.pipelines.commonMongopipeline.commonMongopipeline": 505,
            "easyspider.pipelines.commonMysqlpipeline.commonMysqlpipeline": 510,
        },
    }

    # def start_requests(self):
    #     url = 'https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=reportsSearch.process'
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    #         'content-type': 'application/x-www-form-urlencoded'
    #     }
    #     for year in range(1900, 2019 + 1)[::-1]:
    #         for mounth in range(1, 13):
    #             data = 'rptName=0&reportSelectMonth={}&reportSelectYear={}'.format(mounth, year)
    #
    #             self.put_back_2_start_url(Request(url=url,
    #                                               method='POST',
    #                                               headers=headers,
    #                                               body=data,
    #                                               dont_filter=True))
    #     exit()

    def parse(self, response):
        trs = response.xpath('//table[@id="example_1"]/tbody/tr')
        if trs:
            for tr in trs:
                approval_date = tr.xpath('./td[1]/text()').get()
                drug_name = tr.xpath('./td[2]/a//text()').getall()
                href = tr.xpath('./td[2]/a/@href').get()
                href = response.urljoin(href)
                submission = tr.xpath('./td[3]/text()').get()
                active_ingredients = tr.xpath('./td[4]/text()').get()
                company = tr.xpath('./td[5]/text()').get()
                submission_classification = tr.xpath('./td[6]/text()').get()
                submission_status = tr.xpath('./td[7]/text()').get()
                yield {
                    "approval_date": approval_date,
                    "drug_name": drug_name,
                    "href": href,
                    "submission": submission,
                    "active_ingredients": active_ingredients,
                    "company": company,
                    "submission_classification": submission_classification,
                    "submission_status": submission_status,
                    "easyspider": {
                        "mysql_config": {
                            "db": "baike",
                            "table": "13874_access_list_info"
                        }
                    }
                }


