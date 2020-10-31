#-*- coding:utf-8 -*-
import sys
import pathlib # ptyhon3.4over
import json
import random
from datetime import datetime

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, ERROR

from elasticsearch import Elasticsearch
from elasticsearch import helpers

ABS_PATH = pathlib.Path(__file__).absolute().parent.parent.parent
CONFIG_FILE = ABS_PATH /"config"/"elastic_config.json"

formatter = Formatter('%(asctime)-15s - %(levelname)-8s - %(message)s')
logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
handler.setFormatter(formatter)
logger.setLevel(DEBUG)
logger.addHandler(handler)

class Estool(object):
	_domains = None # domain
	_es = None
	_doc_type="doc"

	###
	#
	def __init__(self):
		super().__init__()
		try:
			with open(CONFIG_FILE, "r") as f:
				self._domains = json.load(f)
#				self._es = Elasticsearch(self._domains)
		except Exception as e:
			print("---------Estool Init error----------")
			logger.error(e)

	####
	# デストラクタ
	def __del__(self):
		try:
			#self._es.close()
			logger.debug("elasticsearch connection close.")
		except Exception as e:
			logger.error(e)


	#データベースへデータを挿入
	def insert_es(self, dbname, doc_):
		try:
			#コネクションの確立
			es = Elasticsearch(self._domains)

			for d in doc_:
				d["@timestamp"] = datetime.now()
				#post
				res = es.index(index=dbname, doc_type=self._doc_type, id=random.randint(1, 100000000), body=d)
				#print(res['result'])
			logger.info("finish: " + str(len(doc_)) )

			#データベースの更新
			es.indices.refresh(index=dbname)

			return True

		except Exception as e:
			logger.error("---------Estool error----------")
			logger.error(e)
			return False


	#データベースへデータを挿入
	def bulk_insert(self, dbname, data):
		try:
			#コネクションの確立
			es = Elasticsearch(self._domains)

			count = 0
			actions = []

			for d in data :
				actions.append({
					"_index" : dbname,
					"_type" : self._doc_type,
					"_id" : random.randint(1, 100000000),
					"_source" : d
					})

				if len(actions) > 1000 :
					helpers.bulk(es,actions)
					actions = []
					count += 1
					logger.debug(count)

			if len(actions) > 0:
				helpers.bulk(es,actions)

			#データベースの更新
			es.indices.refresh(index=dbname)
			logger.info("finish: " + str(len(data) ) )

			return True

		except Exception as e:
			logger.error("---------Estool error----------")
			logger.error(e)
			return False

	###
	#全index取得
	def get_index(self):
		es = Elasticsearch([
			{'host': 'localhost', "port":9200}
		])
		#index取得関数
		index = es.indices.get_alias("*")
		del index[".kibana_1"]
		#for tem in index.keys():
			#print(tem)
		return index


	#query
	#全検索
	query = {}
	def all_search(self, query):
		query["query"]={"match_all":{} }
		return query


	#カラム指定検索：指定したカラムのみ検索する（column:"---","---",……）
	def column_search(self, column, query):
		query["_source"] = [column]
		return query


	#件数指定検索：startからsizeの件数分を表示
	def limit_search(self, start, size, query):
		query["from"] = start
		query["size"] = size
		return query


	#昇順/降順（order: asc/desc）
	def sort_query(self, column, order, query):
		query["sort"] = { column: {"order": order}}
		return query


	#単一条件指定
	def match_search(self, column, data, query):
		query["query"] =  { "match":{"column": data } }
		return query


	####
	# get Data
	def get(self, dbname):
		data = []
		try:
			es = Elasticsearch(self._domains)
			query={
				"query": {
					"match_all": {}
				}
			}
			tmp = es.search(index=dbname, body=query, size=10000)
			#print(tmp)
			print(tmp["hits"]["total"])

			for r in tmp["hits"]["hits"]:
				data.append(r["_source"])
		except Exception as e:
			print("---------Estool error get_all----------")
			logger.error(e)

		return data

	# get all Data
	def get_all(self, dbname):
		result=[]
		data = []
		try:
			es = Elasticsearch(self._domains)

			query={ "query": { "match_all": {} } }
			s_time="2m"

			tmp = es.search(index=dbname, doc_type=self._doc_type, body=query, scroll=s_time, size=10000,  request_timeout=150)
			s_id = tmp['_scroll_id']
			s_size = tmp['hits']['total']
			result.extend ( tmp['hits']['hits'] )

			while (s_size > 0):
				tmp = es.scroll(scroll_id=s_id, scroll=s_time,request_timeout=150)
				s_id = tmp['_scroll_id']
				s_size = len(tmp['hits']['hits'])
				result.extend(tmp['hits']['hits'])

			for r in result:
				data.append(r["_source"])

		except Exception as e:
			logger.error("---------Estool error get_all----------")
			logger.error(e)

		logger.debug("Array data length = "+ str ( len(data) ) )
		return data


	# get all Data
	def get_query(self, dbname, query):
		result=[]
		data = []
		try:
			es = Elasticsearch(self._domains)

			s_time="2m"

			tmp = es.search(index=dbname, doc_type=self._doc_type, body=query, scroll=s_time, size=10000,  request_timeout=150)
			#tmp = es.search(index=dbname, body=query, scroll=s_time, size=10000,  request_timeout=150)

			s_id = tmp['_scroll_id']
			s_size = tmp['hits']['total']
			result.extend ( tmp['hits']['hits'] )

			while (s_size > 0):
				tmp = es.scroll(scroll_id=s_id, scroll=s_time,request_timeout=150)
				s_id = tmp['_scroll_id']
				s_size = len(tmp['hits']['hits'])
				result.extend(tmp['hits']['hits'])

			for r in result:
				data.append(r["_source"])

		except Exception as e:
			logger.error("---------Estool error get_all----------")
			logger.error(e)

		logger.debug("Array data length = "+ str ( len(data) ) )
		return data


	# 条件付きデータ取得
	def get_all_query(self, dbname, query):
		result=[]
		try:
			es = Elasticsearch(self._domains)

			s_time="2m"

			tmp = es.search(index=dbname, doc_type=self._doc_type, body=query, scroll=s_time, size=10000,  request_timeout=150)
			#tmp = es.search(index=dbname, body=query, scroll=s_time, size=10000,  request_timeout=150)
			s_id = tmp['_scroll_id']
			s_size = tmp['hits']['total']
			result.extend ( tmp['hits']['hits'] )

			while (s_size > 0):
				data = es.scroll(scroll_id=s_id, scroll=s_time,request_timeout=150)
				s_id = data['_scroll_id']
				s_size = len(data['hits']['hits'])
				result.extend(data['hits']['hits'])


		except Exception as e:
			logger.error("---------Estool error get_all----------")
			logger.error(e)

		logger.debug("Array data length = "+ str ( len(result)) )
		return result


# test
if __name__=="__main__":
	et = Estool()

	#et.insert_es("test", [{"data":"test"}])
	#et.bulk_insert("aaa", {"a":0})

	import os,sys
	currentdir = os.path.dirname(os.path.abspath(__file__))
	parentdir = os.path.dirname(currentdir)

	print(parentdir)
	sys.path.insert(0,parentdir)

	from util import csv_output

	dbname="population_fluctuation"

	query={
		"query": {
			"bool": {
			  "must":[
					{"match" : {"year": 2015} },
					{"match" : {"label.keyword": "老年人口"} }
				]
			}
		}
	}

	print(dbname)
	#data = et.get_query(dbname, query)
	data = et.get_all(dbname)

	print(data)

	#csv_output.output_csv(data, "population_fluctuation.csv")
