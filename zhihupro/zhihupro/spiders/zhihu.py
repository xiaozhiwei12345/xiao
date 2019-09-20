# -*- coding: utf-8 -*-
from urllib.parse import quote
import re
import time
import scrapy
import json
from zhihupro.items import ZhihuArticleItem, ZhihuAnswerItem, ZhihuComment


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']

    def start_requests(self):
        # 将搜索的关键词放进列表
        keyword_list = ['长投学堂', '长投网']
        for keyword in keyword_list:
            # 根据关键词构造请求url，获得关键词标题
            ajax_url = 'https://www.zhihu.com/api/v4/search_v3?t=general&q={}&correction=1&offset=0&limit=10'.format(
                quote(keyword))
            # 将构造好的url交给parse_ajax函数处理
            yield scrapy.Request(url=ajax_url, callback=self.parse_ajax, meta={'topic': keyword})

    def parse_ajax(self, response):
        # 获取传过来的关键词
        topic = response.meta.get('topic')
        # 将响应的json数据转化为字典
        result = json.loads(response.text)
        # 遍历数据
        for data in result.get('data'):
            if data.get('highlight'):
                # 获取问题标题
                title = data.get('highlight').get('title')
                # 判断问题标题是否包含‘长投’
                if '长投' in title:
                    if data.get('object'):
                        # 判断问题标题的类型是否为'answer'
                        if data.get('object').get('type') == 'answer':
                            # 如果问题类型为answer获取回答id
                            aid = data.get('object').get('id')
                            if data.get('object').get('question'):
                                # 获取问题id
                                qid = data.get('object').get('question').get('id')
                                # 构造详细问题页的url
                                question_url = 'https://www.zhihu.com/question/{}/answer/{}'.format(qid, aid)
                                # 构造回答详细信息的url
                                answer_url = ('https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.'
                                              'is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%'
                                              '2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%'
                                              '2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%'
                                              '2Ceditable_content%2Cvoteup_count%2Creshipment_settings%'
                                              '2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%'
                                              '2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%'
                                              '2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2'
                                              'Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5'
                                              'D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&'
                                              'platform=desktop&sort_by=default'.format(qid))
                                # 将问题详细页url交给parse_question函数处理
                                yield scrapy.Request(
                                    url=question_url,
                                    callback=self.parse_question,
                                    # 将问题id和关键词传递过去
                                    meta={'item': qid, 'topic': topic},
                                    dont_filter=True
                                )
                                # 将回答详细页url交给parse_answer_one函数处理
                                yield scrapy.Request(
                                    url=answer_url,
                                    callback=self.parse_answer_one,
                                    meta={'topic': topic},
                                    dont_filter=True
                                )
        # 判断问题页是否有下一页
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            # 获取问题下一页的url
            next_ajax = result.get('paging').get('next')
            # 将url继续交给parse_ajax处理，直至所有问题处理完整
            yield scrapy.Request(url=next_ajax,
                                 callback=self.parse_ajax,
                                 meta=response.meta,
                                 dont_filter=True)

    def parse_question(self, response):
        # 获取传递过来的关键词
        topic = response.meta.get('topic')
        # 获取响应的字符串内容
        html = response.text
        # 实例化ZhihuArticleItem对象
        articleitem = ZhihuArticleItem()
        # 问题所属关键词
        articleitem['topic'] = topic
        # 问题id 主键
        articleitem['question_id'] = response.meta.get('item')
        # 问题标题
        articleitem['question_title'] = response.xpath('//div[@id="root"]//main//div/h1/text()')[0].extract()
        pattern = re.compile(r'<span class="RichText ztext" itemProp="text">(.*?)</span>')
        # 问题内容
        articleitem['question_content'] = pattern.findall(html)
        # 关注数
        articleitem['attention_counts'] = re.search(
            r'class="NumberBoard-itemValue" title="(.*?)">(.*?)</strong></div></div><div class="NumberBoard-item">',
            response.text).group(2)
        # 浏览数
        articleitem['viewer_counts'] = re.search('.*">被浏览</div>.*title="(\d+)">', html, re.S).group(1) if re.search(
            '.*">被浏览</div>.*title="(\d+)">', html, re.S) else str(0)
        # 总回答数
        articleitem['answer_counts'] = re.search('.*">查看全部.(.*?).个回答<', html, re.S).group(1) if re.search(
            '.*">查看全部.(.*?).个回答<', html, re.S) else str(0)
        # 将实例化对象交给pipelines处理
        print(dict(articleitem))

    def parse_answer_one(self, response):
        # 获取传递过来的关键词
        topic = response.meta.get('topic')
        # 实例化answer对象
        answer = ZhihuAnswerItem()
        # 将响应结果转化为字典
        result = json.loads(response.text)
        if 'data' in result.keys() and result.get('data'):
            for element in result.get('data'):
                eid = element.get('id')
                #关联评论id
                answer['comment_id'] = eid
                #回答所属关键词
                answer['topic'] = topic
                if element.get('question'):
                    # 关联问题id
                    answer['question_id'] = str(element.get('question').get('id'))
                    if 'author' in element.keys() and element.get('author'):
                        # 回答者昵称
                        answer['answer_name'] = element.get('author').get('name')
                        # 回答简介
                        answer['answer_desc'] = element.get('author').get('headline')
                        # 关注人数
                        answer['follower'] = element.get('author').get('follower_count')
                        # 回答内容
                        answer['answer_content'] = element.get('content')
                        # 回答时间
                        answer['answer_time'] = element.get('created_time')
                        pat = re.compile(r'"https.*?jpg"')
                        # 回答内容中的图片
                        answer['answer_image'] = pat.findall(element.get('content'))
                        # 赞同数
                        answer['voteup_count'] = element.get('voteup_count')
                        # 评论数
                        answer['comment_count'] = element.get('comment_count')
                        # 判断回答者是否存在url_token
                        if element.get('author').get('url_token') == "":
                            # 若无，直接将实例化对象交给pipelines处理
                            yield answer
                        else:
                            # 若有，构造回答者详情页的url
                            url_token = element.get('author').get('url_token')
                            people_url = 'https://www.zhihu.com/people/{}/activities'.format(url_token)
                            # 将回答者详情页的url交给parse_anwser_two函数处理
                            yield scrapy.Request(url=people_url,
                                                 callback=self.parse_anwser_two,
                                                 meta={'item': answer},
                                                 dont_filter=True
                                                 )
                # 构造详细评论的url
                comment_url = 'https://www.zhihu.com/api/v4/answers/{}/root_comments?limit=20&offset=0'.format(eid)
                # 将详细评论的url交给parse_comments函数处理
                yield scrapy.Request(url=comment_url,
                                     callback=self.parse_comments,
                                     dont_filter=True,
                                     meta={'eid': eid, 'topic': topic}
                                     )
        # 判断回答是否有下一页
        if 'paging' in result.keys() and result.get('paging').get('is_end') == False:
            # 获取回答下一页的url
            next_link = result.get('paging').get('next')
            # 将url继续交给parse_answer_one处理，直至回答处理完整
            yield scrapy.Request(url=next_link,
                                 callback=self.parse_answer_one,
                                 meta=response.meta,
                                 dont_filter=True
                                 )

    def parse_anwser_two(self, response):
        answer = response.meta['item']
        html = response.text
        pattern = re.compile('>回答<span class="Tabs-meta">(\d+)</span></a>')
        # 回答数量
        answer['answer_num'] = pattern.findall(html)
        # 将实例化对象交给pipelines处理
        print(dict(answer))

    def parse_comments(self, response):
        topic = response.meta.get('topic')
        # 实例化comment对象
        comment = ZhihuComment()
        results = json.loads(response.text)
        if results.get('common_counts') != 0:
            if 'data' in results.keys() and results.get('data'):
                for result in results.get('data'):
                    # 评论所属关键词
                    comment['topic'] = topic
                    # 评论id 主键
                    comment['comment_id'] = response.meta.get('eid')
                    # 评论用户昵称
                    comment['comment_name'] = result.get('author').get('member').get('name')
                    # 评论内容
                    comment['comment_content'] = result.get('content')
                    # 评论时间
                    comment['comment_time'] = result.get('created_time')
                    # 点赞数
                    comment['vote_count'] = result.get('vote_count')
                    if result.get('child_comment_count') != 0:
                        reply_info_list = []
                        for com in result.get('child_comments'):
                            reply_dict = {}
                            # 回复人昵称
                            reply_dict['reply_name'] = com.get('author').get('member').get('name')
                            # 回复人内容
                            reply_dict['reply_content'] = com.get('content')
                            # 回复时间
                            reply_dict['reply_time'] = com.get('created_time')
                            reply_info_list.append(reply_dict)
                            # 所有回复内容信息
                        comment['reply_info'] = reply_info_list
                    # 将实例化对象交给pipelines处理
                    print(dict(comment))
        # 判断评论是否有下一页
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_link = results.get('paging').get('next')
            base = 'https://www.zhihu.com/api/v4/answers'
            # 构造下一页url
            next_link = base + next_link.split('answers')[1]
            # 将下一页url继续交给parse_comments处理
            yield scrapy.Request(url=next_link,
                                 callback=self.parse_comments,
                                 meta=response.meta,
                                 dont_filter=True
                                 )
