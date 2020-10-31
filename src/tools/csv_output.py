#-*- coding:utf-8 -*-
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pathlib # ptyhon3.4over
import codecs
from datetime import datetime

import csv
import pandas as pd
import json
import random

class ResasCSV(object):
	"""docstring for ResasCSV"""
	def __init__(self):
		super().__init__()
		self.__config()
		pass

	#データベースへデータを挿入
	def insert_es(self, dbname, doc_):

		#コネクションの確立
		es = Elasticsearch([
			{'host': 'localhost', "port":9200}
		])

		for d in doc_:
			d["@timestamp"] = datetime.now()
			#post
			res = es.index(index=dbname, doc_type='doc', id=random.randint(1, 100000000), body=d)
			#print(res['result'])
		print("finish")

		#res = es.search(index=dbname, body={"query": {"match_all": {}}})
		#print("Got \n" + str( res) )

		#データベースの更新
		es.indices.refresh(index=dbname)


	#データベースへデータを挿入
	def bulk_insert(self, dbname, data):

		#コネクションの確立
		es = Elasticsearch([
			{'host': 'localhost', "port":9200}
		])

		count = 0
		actions = []

		for d in data :
			actions.append({
				"_index" : dbname,
				"_type" : 'document',
				"_id" : random.randint(1, 100000000),
				"source" : d
				})

			if len(actions) > 400 :
				helpers.bulk(es,actions)
				actions = []
				count += 1
				print(count)

		if len(actions) > 0:
			helpers.bulk(es,actions)

		#データベースの更新
		es.indices.refresh(index=dbname)
		print("finish")

	def json_transfer(self, file_path):

		#pandasによりフレーム形式でcsvファイルの読み込み
		direct = pd.read_csv(file_path,sep=',', encoding="shift-jis")
		#フレーム形式をjson型のような文字列に変換
		tmp = direct.to_json(force_ascii=False, orient='records')
		#文字列をjson形式に変換
		data = json.loads(tmp)

		return data


	#main
if __name__ == '__main__':
	rv = ResasCSV()

	#csvファイルをjson形式に変換
	data_hanabi = rv.json_transfer("まちづくりマップ_通勤通学人口_花火図_都道府県.csv")
	#data_zokusei = json_transfer("まちづくりマップ_通勤通学人口_属性別総数_市区町村.csv")
	#data_area = json_transfer("まちづくりマップ_通勤通学人口_地域別総数_市区町村.csv")

	#データベースにデータを挿入
	#test_es("hanabi",data_hanabi)
	#test_es("zokusei",data_zokusei)
	#test_es("area",data_area)
	rv.bulk_insert("hanabi",data_hanabi)


