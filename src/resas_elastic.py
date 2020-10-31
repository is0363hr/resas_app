#-*- coding:utf-8 -*-

import pathlib # ptyhon3.4over
import configparser
import json
import codecs
from datetime import datetime
import urllib.request as request
import urllib.parse as parse
#from logging import config
#from logging import getlogger

from elasticsearch import Elasticsearch
from elasticsearch import helpers

ABS_PATH = pathlib.Path(__file__).absolute().parent.parent
APIKEY_FILE= ABS_PATH /"config"/"APIKEY"
CITIES_FILE= ABS_PATH /"config"/"cities.json"
PREF_FILE= ABS_PATH /"config"/"prefectures.json"
#print(APIKEY_FILE)

class ResasAPI(object):

	alias_url = "https://opendata.resas-portal.go.jp/"
	pref = None   # 都道府県コード
	cities = None # 市町村コード

	def __init__(self):
		super().__init__()
		self.__config()
		pass

	# config 
	def __config(self):
		try:
			with open(APIKEY_FILE, mode="r") as file:
				self.headers = { "X-API-KEY":file.read() }

			with open(CITIES_FILE, "r", encoding='utf8') as f:
				self.cities = json.load(f)

			with open(PREF_FILE, "r", encoding='utf8') as f:
				self.pref = json.load(f)

		except Exception as e:
			print("---Resas Config Error---")
			print(e)
			raise

	############################
	#	ちょっとしたparser
	def _parse_url(self, url):
		if url.startswith("/"):
			return self.alias_url + url[1:] # 先頭の/を外す
		else:
			return self.alias_url + url

	###################
	# Get Method
	def get(self, url_, params="", headers=None ):
		data = None
		if params != "":
			p = parse.urlencode(params)
			url_ += "?" + p
		
		print(url_)

		# request to REST API
		try:
			req = request.Request(url=url_, headers=self.headers, method="GET")
			with request.urlopen(req) as res:
				data = json.loads( res.read() )

		except Exception as e:
			print("---Resas GET Error---")
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
			print("---Resas POST Error---")
			print(e)
		finally:
			pass
		

	#####################
	# put
	# data's type string(=json.dumps() )
	def put(self, url, data):
		headers = self.headers
		headers["Content-Type"] = "application/json"
		
		try:
			req = request.Request(url=self.alias_url+url, data=data.encode(), headers=headers, method="PUT" )
			res = request.urlopen(req)
			print( json.loads( res.read() ) )

		except Exception as e:
			print("---Resas PUT Error---")
			print(e)
		finally:
			pass

	############################
	# Convert Prefecture Code
	# 都道府県コード or 名を出力する
	def convertPref(self, Code=None, Name=None):
		try:
			if Code is not None:
				codeList = {x["prefCode"] : x["prefName"] for x in self.pref}
				return codeList[Code]

			elif Name is not None:
				nameList = {x["prefName"] : x["prefCode"] for x in self.pref}
				return nameList[Name]

		except Exception as e:
#			raise e
			return Code or Name

	############################
	# Convert City Code
	# 市町村コード or 名を出力する
	def convertCity(self, pref, Code=None, Name=None):
		cities = self.cities[int(pref)-1]
		try:
			if Code is not None:
				codeList = {x["cityCode"] : x["cityName"] for x in cities}
				return codeList[str(Code)]

			elif Name is not None:
				nameList = {x["cityName"] : x["cityCode"] for x in cities}
				return nameList[Name]
		except Exception as e:
		#	raise e
			return Code or Name

	############################
	# 新卒者就職・進学 2000 ~ 2016
	#
	# method: GET
	# url: api/v1/employEducation/localjobAcademic/toTransition
	#
	#def employ(self,prefCode,dMethod,matter,classifi,dType,gender):
	def employ(self,prefCode,dMethod,matter,classifi,dType,gender):
		api = "api/v1/employEducation/localjobAcademic/toTransition"
	
		params = {
			"prefecture_cd": prefCode,	# 都道府県
			"displayMethod": dMethod,	# 0:実数 1:就職率・進学率
			"matter": matter,	# 0:地元就職 1:流出 2:流入 3:純流入
			"classification": classifi,	# 0:就職・進学の合計 1:進学 2:就職
			"displayType":dType,	# 00:すべての就職・進学 10:すべての進学 11:大学進学 12:短期大学進学 20:就職
			"gender":gender		# 0:総数 1:男性 2:女性
		}
	

		tmp = self.get(self._parse_url(api), params)

		data = []
		
		
		for value in tmp["result"]["changes"]:
			for chang_d in value["data"]:
				d = {
					"label": value["label"],
					"prefCode": value["prefCode"],
					"year": chang_d["year"],
					"value": chang_d["value"]
				}
				data.append(d)


		print(data)
		return data

	############################
	# 指定地域への国籍別訪問者数 2011.2q ~ 2016 3q
	#
	# method: GET
	# url: api/v1/tourism/foreigners/forFrom
	# year -1~input_year 
	# e.g. input:2012 getdata 2011~2012 sum=8quarter
	# addArea Value is SUM. 市町村のデータは合算値で値が渡される。
	#
	def forFrom(self, year, prefCode, purpose, addArea=None):
		api = "api/v1/tourism/foreigners/forFrom" # api url

		params = {
			"year": year, # 2011 ~ 2016
			"prefCode": prefCode, #27:Osaka 都道府県
			"purpose": purpose # 1:all or 2: only leisure, Sightseeing
		}

		if addArea is not None:
			params["addArea"] = addArea

		tmp = self.get(self._parse_url(api), params )

		data = []
		print(tmp)

		for value in tmp["result"]["changes"]:
			#print(value)
			for chan_d in value["data"]:
				#print(chan_d)
				d = {
					"prefCode": tmp["result"]["prefCode"],
					"prefName": tmp["result"]["prefName"],
					"purpose": tmp["result"]["purpose"],
					"countryCode": value["countryCode"],
					"countryName": value["countryName"],
					"term": datetime( chan_d["year"], chan_d["quarter"]*3, 1, 0, 0, 0, 0),
					"value": chan_d["value"]
				}
				data.append(d)

		return data

	##############################
	# 昼間人口・夜間人口の地域別構成割合 2010 or 2015
	# method: GET
	# url: api/v1/townPlanning/commuteSchool/areaPopulationCircle
	# year: 2010 or 2015 
	# mode 0: 全国 1: prefecture(都道府県) 2:cities
	# e.g. input:2012 getdata 2011~2012 sum=8quarter
	#
	def commute(self, mode, year, prefCode, cityCode="-"):
		api = "api/v1/townPlanning/commuteSchool/areaPopulationCircle"
		#リクエストの作成
		if cityCode=="":
			cityCode = "-"
		params = {
			"mode": mode, # 0:全国を表示する 1:都道府県単位で表示する 2:市区町村単位で表示する
			"year": year, # 2010 or 2015
			"prefecture_cd": prefCode, 
			"city_cd": cityCode # all=> - mode:2の時には使用できない
		}
		#レスポンスの受け取り
		tmp = self.get(self._parse_url(api), params )

		##print(tmp)
		data = []

		cityName = cityCode
		if mode == 2: #市町村コード取得時のみ
			cityName = self.convertCity(int(pref), Code=cityCode)
		# noon
		for value in tmp["result"]["noonData"]:
			#print(value)
			d = {
				"year" : year,
				"prefCode": tmp["result"]["pref"],
				"cityCode": tmp["result"]["city"],
				"cityName": cityName,
				"mode": tmp["result"]["mode"],
				"noonDataSum": tmp["result"]["noonDataSum"],
				"nightDataSum": tmp["result"]["nightDataSum"],
				#dayNightRate: 夜間人口100人当たりの昼間人口の割合であり、100を超えているときは通勤・通学人口の流入超過、100を下回っているときは流出超過を示している。 
				"dayNightRate": tmp["result"]["dayNightRate"], 
				"noonCode": value["code"],
				"noonName": value["name"],
				"noonValue": value["value"],
				#"tooltip": value["tooltip"],
				"noonRate": value["rate"]
			}
			data.append(d)

		# night
		for value in tmp["result"]["nightData"]:
			#print(value)
			d = {
				"year" : year,
				"prefCode": tmp["result"]["pref"],
				"cityCode": tmp["result"]["city"],
				"cityName": cityName,
				"mode": tmp["result"]["mode"],
				"noonDataSum": tmp["result"]["noonDataSum"],
				"nightDataSum": tmp["result"]["nightDataSum"],
				"dayNightRate": tmp["result"]["dayNightRate"],
				"nightCode": value["code"],
				"nightName": value["name"],
				"nightValue": value["value"],
				"nightRate": value["rate"]
			}
			data.append(d)

		return data


	##############################
	# 人口構成
	# method: GET
	# url: api/v1/population/composition/perYear
	# year: 1980~2045(5年毎)
	#　addArea Value is SUM. 市町村のデータは合算値で値が渡される。
	def population(self,  prefCode, cityCode, addArea=None):
		api = "api/v1/population/composition/perYear" # api url

		if cityCode=="":
			cityCode="-"
		params = {
			"prefCode": prefCode, #27:Osaka 都道府県
			"cityCode": cityCode # 市町村コード
		}

		if addArea is not None:
			params["addArea"] = addArea

		tmp = self.get(self._parse_url(api), params )
		data = []
		try:
			for value in tmp["result"]["data"]:
				#print("----------------------")
				#print(value)
				for value2 in value["data"]:
					#print("___________________________")
					#print(value2)
					d = {
						"prefCode": prefCode, #27:Osaka
						"prefName": prefName,
						"cityCode": cityCode,
						"cityName": cityName,
						"boundaryYear": tmp["result"]["boundaryYear"],
						"label": value["label"],
						"year":  value2["year"],
						"value": value2["value"]
					}
					if "rate" in value2:
						d["rate"] = value2["rate"]
					data.append(d)
		except Exception as e:
			print(e)

		return data

	##############################
	# 人口の増減
	# method: GET
	# url: api/v1/population/composition/perYear
	# year: 1980~2045(5年毎)
	#　addArea Value is SUM. 市町村のデータは合算値で値が渡される。
	def population_fluctuation(self, prefName, prefCode, cityName, cityCode="-", addArea=None):
		api = "api/v1/population/sum/perYear" # api url

		if cityCode=="":
			cityCode="-"
		params = {
			"prefCode": prefCode, #27:Osaka 都道府県
			"cityCode": cityCode # 市町村コード
		}

		if addArea is not None:
			params["addArea"] = addArea

		tmp = self.get(self._parse_url(api), params )
		data = []
		try:
			for value in tmp["result"]["bar"]["data"]:
				#print("----------------------")
				#print(value)
				for value2 in value["class"]:
					#print("___________________________")
					#print(value2)
					d = {
						"prefCode": prefCode, #27:Osaka
						"prefName": prefName,
						"cityCode": cityCode,
						"cityName": cityName,
						"year":  value["year"],
						"sum"	: value["sum"],
						"boundaryYear": tmp["result"]["line"]["boundaryYear"],
						"label": value2["label"],
						"value": value2["value"]
					}
					data.append(d)
		except Exception as e:
			print(e)

		return data
    
    ##############################
    # 入国空港・出国空港内訳
    # method: Get
    # url: api/v1/tourism/airport/forCircle
    # year 2014年~2016年(四半期ごと)
	def forCircle(self, year, halfPeriod, prefCode):
		api="api/v1/tourism/airport/forCircle"

		params = {
			"year": year,  #表示年
			"halfPeriod": halfPeriod,  #表示四半期 1:すべての期間（デフォルト設定） 
			                           #2:1-3月期 3: 4-6月期 4: 7-9月期 5: 10-12月期
			"prefCode": prefCode,  #都道府県コード
		}

		tmp = self.get(self._parse_url(api), params)
		data = []
		from time import sleep
		sleep(15)
		print(tmp)
		for chan_d in tmp["result"]["entryAndDepartureAirport"]:

			d = {
				"year": tmp["result"]["year"],
				"halfPeriod": tmp["result"]["halfPeriod"],
				"prefCode": tmp["result"]["prefCode"], #27:Osaka
				"entryAirportCode": chan_d["entryAirportCode"],
				"entryAirportName": chan_d["entryAirportName"],
				"departureAirportCode": chan_d["departureAirportCode"],
				"departureAirportName": chan_d["departureAirportName"],
				"value": chan_d["value"],
				"rate": chan_d["rate"]
				}
			data.append(d)

		for chan_d in tmp["result"]["entryAirport"]:
			d = {
				"year": tmp["result"]["year"],
				"halfPeriod": tmp["result"]["halfPeriod"],
				"prefCode": tmp["result"]["prefCode"], #27:Osaka
				"airportCode": chan_d["airportCode"],
				"airportName": chan_d["airportName"],
				"value": chan_d["value"],
				"rate": chan_d["rate"]
				}
			data.append(d)

		for chan_d in tmp["result"]["departureAirport"]:
			d = {
				"year": tmp["result"]["year"],
				"halfPeriod": tmp["result"]["halfPeriod"],
			    "prefCode": tmp["result"]["prefCode"], #27:Osaka
				"airportCode": chan_d["airportCode"],
				"airportName": chan_d["airportName"],
				"value": chan_d["value"],
				"rate": chan_d["rate"]
				}
			data.append(d)
		return data

def test_es(dbname, _doc):
	import random

	es = Elasticsearch([
		{'host': 'localhost', "port":9200}
	])



	test_id = random.randint(1, 100000000)

	# insert
	res = es.index(index=dbname, doc_type='doc', id=test_id, body=_doc)
	print(res['result'])

	res = es.get(index=dbname, doc_type='doc', id=test_id)
	print("get From Elasticsearch")
	print(res['_source'])

	es.indices.refresh(index=dbname)

	#res = es.search(index="test-resas", body={"query": {"match_all": {}}})
	#print("Got %d Hits:" % res['hits']['total'])
	#for hit in res['hits']['hits']:
	#	print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
	

##########
# file出力用
def append_json_to_file(_dict, path_file):
	with open(path_file, 'ab+') as f:					# ファイルを開く
		f.seek(0,2)															# ファイルの末尾（2）に移動（フォフセット0）	
		if f.tell() == 0 :											 # ファイルが空かチェック
			f.write(json.dumps([_dict]).encode())	# 空の場合は JSON 配列を書き込む
		else :
			f.seek(-1,2)													 # ファイルの末尾（2）から -1 文字移動
			f.truncate()													 # 最後の文字を削除し、JSON 配列を開ける（]の削除）
			f.write(' , '.encode())								# 配列のセパレーターを書き込む
			f.write(json.dumps(_dict).encode())		# 辞書を JSON 形式でダンプ書き込み
			f.write(']'.encode())									# JSON 配列を閉じる
	return f.close() # 連続で追加する場合は都度 Open, Close しない方がいいかも



#############################
# main 
# test code
if __name__=="__main__":

	ra = ResasAPI()

	# prefecture list
	# url = "api/v1/prefectures"
	#data = ra.get(ra._parse_url(url) )

	##############
	# Cities list
	"""
	url = "api/v1/cities"

	#params ={ "prefCode": 27 }
	#data = ra.get(ra._parse_url(url), params)
	#print(type( data["result"] ) )
	

	for i in range(1,48): # 1~47
		params ={ "prefCode": i }
		data = ra.get(ra._parse_url(url), params)
		append_json_to_file(data["result"], "cities.json")
	"""

	#####################
	# get Data from forfrom
	# 
	"""
	data = ra.forFrom(2012, 13, 1)	
	print(data)
	print(type(data) )
	dbname = "resas-forfrom"
	

	if type(data) is str:
		exit()
	"""

	# 事前にとっておいた都道府県コードをファイルから取得
	pref = None
	with open(PREF_FILE, "r", encoding='utf8') as f:
		pref = json.load(f)

	# 事前にとっておいた市町村コードをファイルから取得
	cities = None
	with open(CITIES_FILE, "r", encoding='utf8') as f:
		cities = json.load(f)


	import random
	from tools import estool
	et = estool.Estool()

	#es = Elasticsearch([ {'host': 'localhost', "port":9200} ])
	dbname = "population"

	
	for i in range(47):
		for c in cities[i]:
			data = ra.population( ra.convertPref(i+1),c["prefCode"], c["cityName"], c["cityCode"])
			#data = ra.population_fluctuation( ra.convertPref(i+1),c["prefCode"], c["cityName"], c["cityCode"] )
			#data = ra.commute(2,2015, c["prefCode"], c["cityCode"])
			#print(data)

			#for d in data:
			#	d["@timestamp"] = datetime.now()
			#	res = es.index(index=dbname, doc_type='doc', id=random.randint(1, 100000000), body=d)
			#es.indices.refresh(index=dbname)

			et.bulk_insert(dbname, data)
	
	"""

	#data = ra.population(27, 27203)
	#data = ra.commute(2, 2015, 27, 27223)
	##print(data)
	
#	data = ra.employ(13,"0","1","0","00","0")
#	print(data)

#	test_es("test", data)

	#
	# test data
	"""
	
	#dbname = "test"
	#bulk insert
	es = Elasticsearch([
		{'host': 'localhost', "port":9200}
	])

	#helpers.bulk(es, data["result"])

	for d in data:
		d["@timestamp"] = datetime.now()
		res = es.index(index=dbname, doc_type='doc', id=random.randint(1, 100000000), body=d)
		#print(res['result'])
	print("finish")

	#res = es.search(index=dbname, body={"query": {"match_all": {}}})
	#print("Got \n" + str( res) )

	es.indices.refresh(index=dbname)
#	"""

	"""
	# test kibana api
	import kibana_api

	ig = kibana_api.IndexPatternGenerator()
	vg = kibana_api.VisualizationGenerator()

	ka = kibana_api.KibanaAPI()
	ea = kibana_api.ElasticAPI()

	print("test : " + ig.alias)

	mappings = ea.get_db_mapping(dbname)
	print("mappings:\n" + str( mappings) )

	iid = "resas-forfrom-index"
	vid = "resas-forfrom-graph"

	# make index
	ig_data = ig.genarate("resas-forfrom", mappings, False, iid)
	ka.post(ig.alias + iid , ig_data)

	# make visual
	vg_data = vg.genarate(vid, ["value"], iid)
	ka.post(vg.alias + vid, vg_data)
	"""

