# -*- coding: utf-8 -*-

from pymongo import (MongoClient, ASCENDING)
from taicang.utils import (now_datetime, now_date)
from taicang.settings import (JS_TC_XF_ROOM, JS_TC_XF_PROJECT, JS_TC_XF_BUILD)
from taicang.settings import (MONGODB_HOST, MONGODB_PORT, MONGODB_DBNAME, MONGODB_USER, MONGODB_PWD)


class MongoDBUtils(object):

    def __init__(self):
        self.client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
        self.db = self.client[MONGODB_DBNAME]
        self.db.authenticate(MONGODB_USER, MONGODB_PWD)

    def close_client(self):
        self.client.close()

    def get_row(self, collection, filter):
        collect = self.db[collection]
        return collect.find_one(filter)

    def add_or_update(self, collection, filter, row):
        collect = self.db[collection]
        filter_row = self.get_row(collection, filter)
        if not filter_row:
            cur_datetime = now_datetime()
            row['iStatus'] = 1
            row['sCreateTime'] = cur_datetime
            row['sUpdateTime'] = cur_datetime
            doc_id = collect.insert_one(row).inserted_id
        else:
            doc_id = filter_row['_id']
            row = self.filter_row_void(row)
            row['sUpdateTime'] = now_datetime()
            collect.update_one({'_id': filter_row['_id']}, {'$set': row})
        # 房间状态变化监测
        if collection == JS_TC_XF_ROOM:
            cur_room_state_color = row.get('sRoomState', '')
            pre_room_state_color = filter_row.get('sRoomState', '') if filter_row else ''
            if cur_room_state_color != '' and cur_room_state_color != pre_room_state_color:
                row['sDate'] = now_date()
                filter.update({'sDate': now_date()})
                self.add_row("%s_daily" % collection, filter, row)
        return doc_id

    def add_row(self, collection, filter, row):
        cur_datetime = now_datetime()
        row['iStatus'] = 1
        row['sCreateTime'] = cur_datetime
        row['sUpdateTime'] = cur_datetime
        collect = self.db[collection]
        filter_row = self.get_row(collection, filter)
        if not filter_row:
            doc_id = collect.insert_one(row).inserted_id
        else:
            doc_id = filter_row['_id']
        return doc_id

    def upd_row(self, collection, filter, upd_data):
        collect = self.db[collection]
        result = collect.update_one(filter, {'$set': upd_data})
        return result

    def filter_row_void(self, row):
        for key in list(row.keys()):
            if not row.get(key) and row.get(key) != 0:
                del row[key]
        return row

    # 获取项目id
    def get_project_id(self, crawl_col, crawl_time, limit):
        filter = {'$or': [{crawl_col: {'$exists': False}}, {crawl_col: {'$lt': crawl_time}}]}
        collection = self.db[JS_TC_XF_PROJECT]
        return collection.find(filter).limit(limit).sort(crawl_col, ASCENDING)

    # 获取楼栋id
    def get_build_id(self, crawl_col, crawl_time, limit):
        filter = {'$or': [{crawl_col: {'$exists': False}}, {crawl_col: {'$lt': crawl_time}}]}
        collection = self.db[JS_TC_XF_BUILD]
        return collection.find(filter).limit(limit).sort(crawl_col, ASCENDING)

    # 获取房间id
    def get_room_id(self, crawl_col, crawl_time, limit):
        filter = {'$or': [{crawl_col: {'$exists': False}}, {crawl_col: {'$lt': crawl_time}}]}
        collection = self.db[JS_TC_XF_ROOM]
        return collection.find(filter).limit(limit).sort(crawl_col, ASCENDING)
