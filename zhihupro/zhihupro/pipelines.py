# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from zhihupro.items import ZhihuArticleItem, ZhihuAnswerItem, ZhihuComment
import pymongo
client = pymongo.MongoClient(host='172.168.1.24', port=27017)
db = client.zhihu


class ZhihuproPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, ZhihuArticleItem):
            article = dict(item)
            collection = db.question
            if collection.update_one({'question_id': article.get('question_id')}, {'$set': article}, upsert=True):
            # if collection.update_one(article, {'$set': article}, upsert=True):
                print('存入成功')
            else:
                print('存入失败')
        elif isinstance(item, ZhihuAnswerItem):
            answer_data = dict(item)
            collection = db.answer
            if collection.update_one({'comment_id': answer_data.get('comment_id')}, {'$set': answer_data}, upsert=True):
            # if collection.update_one(answer_data, {'$set': answer_data}, upsert=True):
                print('存入成功')
            else:
                print('存入失败')
        elif isinstance(item, ZhihuComment):
            comment_data = dict(item)
            collection = db.comment
            if collection.update_one({'id': comment_data.get('id')}, {'$set': comment_data}, upsert=True):
            # if collection.update_one(comment_data, {'$set': comment_data}, upsert=True):
                print('存入成功')
            else:
                print('存入失败')
        return item
