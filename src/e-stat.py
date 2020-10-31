#-*- coding:utf-8 -*-

import pathlib # ptyhon3.4over
import configparser
import csv
import json
import codecs
from datetime import datetime
import urllib.request as request
import urllib.parse as parse
#from logging import config
#from logging import getlogger

import numpy as np
import pandas as pd

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from tools import estool

ABS_PATH = pathlib.Path(__file__).absolute().parent.parent
APIKEY_FILE= ABS_PATH /"config"/"ESTATKEY"
CITIES_FILE= ABS_PATH /"config"/"cities.json"


class EstatAPI(object):

	alias_url = "http://api.e-stat.go.jp/rest/2.1/app/getSimpleStatsData" # csv形式
	params = {
		"appId"	: "",
		"lang"	: "J",
	}

	def __init__(self):
		super().__init__()
		self._config()
		pass

	# config 
	def _config(self):
		try:
			with open(APIKEY_FILE, mode="r") as file:
				self.params["appId"] = file.read()
		except Exception as e:
			print("---Estat Config Error---")
			print(e)
			raise

	###################
	# Get Method
	def get(self, params="", headers=None ):
		data = None
		if params == "":
			return None

		p = parse.urlencode(params)
		url_ = self.alias_url + "?" + p
		
		print(url_)

		# request to REST API
		try:
			req = request.Request(url=url_, method="GET")
			with request.urlopen(req) as res:
				data = res.read()

		except Exception as e:
			print("---Estat GET Error---")
			print(e)

		finally:
			return data

	####################
	# POST Method
	# data's type bytes
	def post(self, url, data):
		headers = self.headers
		headers["Content-Type"] = "application/json"
		
		print(url)

		try:
			req = request.Request(url=self.alias_url+url, data=data.encode(), headers=headers, method="POST" )
			res = request.urlopen(req)
			print( json.loads( res.read() ) )
		except Exception as e:
			print("---Estat POST Error---")
			print(e)
		finally:
			pass

	def getData(self, statsDataId):
		et = estool.Estool()

		result = []
		params = self.params
		params["statsDataId"] = statsDataId
		params["metaGetFlg"] = "N"
		params["cntGetFlg"] = "N"
		params["sectionHeaderFlg"] = 1 # 省略可、CSVのヘッダー出力設定
		params["lvArea"] = 3	# 検索レベル 1:全国 2:都道府県 3:市・群 4:町・村
		params["startPosition"] = 1

		# main loop
		for i in range(2):
	#		pass
			tmp = self.get(params=params)
			print(tmp)

			tmp = tmp.decode().replace("\"", "")
			lines = tmp.split("\n")

			state = lines[:lines.index("VALUE")]
			data = lines[lines.index("VALUE")+1:] # VALUEの次からデータ

			print(state)
			print(data[0].split(","))

			# state
			for s in state:
				# NEXT_KEYの抽出
				print(s)
				if "NEXT_KEY" in s:
					a = s.split(",")
					params["startPosition"] = a[1]
					break

			print(params["startPosition"])

			# parse data
			l = [i.split(",") for i in data]

			#	if i == "VALUE":
			print(len(l))
			if len( l[-1] ) <= 1: # 末尾のデータをチェック。
				l.pop()
			print(len(l))

			columns = l.pop(0)
			print(columns)
			print(len(l))

			result.extend(l)

		df = pd.DataFrame(result, columns=columns)
		print(df.head())

		df = df.astype({"value":int})
		print(df.dtypes)

		d = json.loads( df.to_json(force_ascii=False, orient='records') )
		print(d[0])
		print(d[1])
		print(type(d))

		et.bulk_insert("estattest", d)

#		return tmp

	################################
	# 人口動態調査
	#
	# statsDataId = 0003268662
	#

#app/getSimpleStatsData?appId=&lang=J&statsDataId=0003153342&metaGetFlg=Y&cntGetFlg=N&sectionHeaderFlg=1


if __name__=="__main__":
	ea = EstatAPI()

#	ea.getData("0003268662")

	ea.getData("0201010000000010000")