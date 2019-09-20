# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ZhihuArticleItem(scrapy.Item):
    topic = scrapy.Field()  # 主题
    question_id = scrapy.Field()  # 主键
    question_title = scrapy.Field()  # 问题标题
    question_content = scrapy.Field()  # 问题内容
    attention_counts = scrapy.Field()  # 关注数
    viewer_counts = scrapy.Field()  # 浏览数
    answer_counts = scrapy.Field()  # 总回答数


class ZhihuAnswerItem(scrapy.Item):
    topic = scrapy.Field()  # 主题
    question_id = scrapy.Field()  # 关联问题id
    answer_name = scrapy.Field()  # 回答者昵称
    answer_desc = scrapy.Field()  # 回答简介
    answer_num = scrapy.Field()  # 回答数量
    follower = scrapy.Field()  # 关注人数
    answer_content = scrapy.Field()  # 回答内容
    answer_image = scrapy.Field()  # 内容中的图片
    voteup_count = scrapy.Field()  # 赞同数
    comment_count = scrapy.Field()  # 评论数
    comment_id = scrapy.Field()  # 关联评论id
    answer_time = scrapy.Field()  #回答时间


class ZhihuComment(scrapy.Item):
    topic = scrapy.Field()  # 主题
    comment_id = scrapy.Field()  # 主键
    comment_name = scrapy.Field()  # 评论用户昵称
    comment_content = scrapy.Field()  # 评论用户内容
    comment_time = scrapy.Field()  # 评论时间
    vote_count = scrapy.Field()  # 点赞数
    reply_name = scrapy.Field()  # 回复人昵称
    reply_content = scrapy.Field()  # 回复人内容
    reply_time = scrapy.Field()  # 回复人时间
    reply_info = scrapy.Field()  # 所有回复信息
    id = scrapy.Field()
