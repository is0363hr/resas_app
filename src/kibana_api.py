#-*- coding:utf-8 -*-9
import pathlib # ptyhon3.4over
import configparser
import json
import codecs
import urllib.request as request
import urllib.parse as parse
from logging import config
from logging import getLogger

ABS_PATH = pathlib.Path(__file__).absolute().parent.parent
CONFIG_FILE = ABS_PATH /"config"/"kibana.conf"
LOGGING_FILE = ABS_PATH /"config"/"logging.conf"
COLOR_SCHEMA = ["#508642","#447EBC","#C15C17""#CCA300","#0A50A1", "#6D1F62", "#584477" ]

config.fileConfig(LOGGING_FILE)
LOG = getLogger(__name__)

####################
#
#
class IndexPatternGenerator(object):
	"""
	###  Sample data
	#		"type": "index-pattern",
	#		"id" : "test-pattern"
	json_data = { 
		"attributes": {
			"title": "test*",
			"timeFieldName": "@timestamp", # option
			"fields": '[{"name":"filename","type":"string","count":0,"scripted":false,"searchable":true,"aggregatable":false,"readFromDocValues":false},{"name":"filename.keyword","type":"string","count":0,"scripted":false,"searchable":true,"aggregatable":true,"readFromDocValues":true}]' 
			# fields option
		}
	}
	"""

	# index-pattern REST API url
	alias = "api/saved_objects/index-pattern/"

	def __init__(self):
		super().__init__()

	##############
	#  ganerate fields data from db's mappings
	def _generate_fields(self, mappings):
		s = []

		for key, value in mappings.items():
			d = {
				"name": key,
				"count": 0,
				"scripted": False,
				"searchable": True,
				"aggregatable": True,
				"readFromDocValues": True
			}
			# Numeric => long(integer), float
			if value["type"] in ("long", "float"):
				d["type"] = "number"

			elif value["type"] == "text":
				d["type"] = "string"
				d["aggregatable"] = False
				d["readFromDocValues"] = False

				# feilds
				d2 = {
					"name": key+".keyword",
					"type": "string",
 					"count": 0,
					"scripted": False,
					"searchable": True,
					"aggregatable": False,
					"readFromDocValues": False
				}
				s.append(d2)

			else:
				# Datetime => date
				# boolean
				d["type"] = value["type"]

			s.append(d)
		
		return json.dumps(s)

	##############
	# generate json data for Kibana REST API
	def genarate(self, title, mappings, bulk=False, id_="test-pattern" ):
		json_data = {}
		json_data["attributes"] = {}

		if bulk:
			json_data["type"] = "index-pattern"
			json_data["id"] = id_
			pass

		json_data["attributes"]["title"] = title
		json_data["attributes"]["timeFieldName"] = "@timestamp"
		json_data["attributes"]["fields"] = self._generate_fields(mappings)

		LOG.debug(json_data)
		
		return json.dumps(json_data)

####
# Visualization Generator(Line)
#
class VisualizationGenerator(object):
	#	"id": "test_BatteryVehicleLog_EnergyConsumpotion_W",
	#	"type": "visualization",
	"""
	test_data = {
		"attributes": {
			"title": "123",
			"description": "",
			"visState": "{}",
			"uiStateJSON": "{}",
			"kibanaSavedObjectMeta": { "searchSourceJSON": "{}" }
		}
	}
	"""
	# index-pattern REST API url
	alias = "api/saved_objects/visualization/"

	def __init__(self):
		super().__init__()

	def _vis_genearate(self, title, type_, columns):
		vis = {
			"title": title,
			"type": type_
		}

		### 
		# paramsの設定
		params = {
			"addLegend": True,
	    "addTimeMarker": False,
	    "addTooltip": True,
	    "legendPosition": "right", # ラベルの位置
			"type": type_,
			"times": [],
			"grid": {
				"categoryLines": False,
      	"style": { "color": "#eee" }
      }
		}
		# 横(カテゴリ)軸の設定
		params["categoryAxes"]=[
			{
        "id": "CategoryAxis-1",
        "title": {},
        "type": "category",
        "show": True,
        "style": {},
        "position": "bottom",
        "scale": { "type": "linear" },
        "labels": {
          "show": True,
          "truncate": 100
        },
      }
		]

		# 縦データ群の縦軸設定
		params["seriesParams"] = []
		count = 1
		for column in columns:
			if count == 2 : continue # id=2は横軸に使われているみたい
			d ={
				"data": {
					"id": str(count),
					"label": column
				},
				"drawLinesBetweenPoints": True,
				"mode": "normal",
				"show": True,
				"showCircles": True,
				"type": type_,
				"valueAxis": "ValueAxis-1"
			}
			if count==1: d["show"] = "true"

			params["seriesParams"].append(d)
			count += 1

		# 縦軸の設定
		params["valueAxes"]=[{
			"id": "ValueAxis-1",
			"name": "LeftAxis-1",
      "type": "value",
      "position": "left",
      "show": True,
      "style": {},
			"labels": {
				"filter": False,
				"rotate": 0,
				"show": True,
				"truncate": 100
			},
      "scale": {
        "mode": "normal",
        "type": "linear"
      },
      "title": { "text": "Vertical" },
		}]

		vis["params"] = params

		###
		# aggsの設定
		aggs = [{
			# 横軸の設定
			"id": "2", 
      "enabled": True,
      "type": "date_histogram",
      "schema": "segment",
      "params": {
        "field": "term",
        "timeRange": {
          "from": "now-30d",
          "to": "now",
          "mode": "quick"
        },
        "useNormalizedEsInterval": True,
        "interval": "M",
        "time_zone": "Asia/Tokyo",
        "drop_partials": False,
        "customInterval": "3 Monthly",
        "min_doc_count": 1,
        "extended_bounds": {},
        "customLabel": "Time"
      }
		}]

		count = 1
		for column in columns:
			if count == 2 : continue # id=2は横軸に使用
			d = {
				"id": str(count),
				"enabled": True,
				"type": "max",
				"schema": "metric",
				"params": {
					"field": column,
					"customLabel": column
				}
			}

			aggs.append(d)
			count +=1

		vis["aggs"] = aggs

		return json.dumps(vis)

	def _uistate_generate(self, columns):
		# set colors
		colors = {}
		for index, column in enumerate(columns):
			colors[column] = COLOR_SCHEMA[index]

		d = {"vis": {"colors": colors } }

		return json.dumps(d)


	def genarate(self, title, mappings, index_pattern=None, bulk=False, id_=None ):
		json_data = {}
		json_data["attributes"] = {}

		if bulk: # bulk object
			json_data["type"] = "visualization"
			if id_ is not None:
				json_data["id"] = id_

		# main genarate
		json_data["attributes"]["title"] = title
		json_data["attributes"]["description"] = ""
		
		if index_pattern is not None:
			
			# vis
			json_data["attributes"]["visState"] = self._vis_genearate(title, "line", mappings)

			# ui
			json_data["attributes"]["uiStateJSON"] = "{}"
			#json_data["attributes"]["uiStateJSON"] = self._uistate_generate(["column1"])

			# search objects
			d = {
				"index":index_pattern,
				"query":{
					"language":"lucene",
					"query":""
				},
				"filter":[]
			}
			json_data["attributes"]["kibanaSavedObjectMeta"] = {}
			json_data["attributes"]["kibanaSavedObjectMeta"]["searchSourceJSON"] = json.dumps(d)

		print("VIS data")
		print(json_data)

		return json.dumps(json_data)
	

############
#
#
class DashboardGenerator(object):

	def __init__(self):
		super().__init__()

	def ganerate(self, id_, title, columns, bulk=False):
		json_data = {}

		if bulk:
			json_data.title = title
			json_data.timeFieldName = "@timestamp"
			pass

		json_data.fields = self._generate_fields(columns)

		return self.json_data

############
# 
class KibanaAPI(object):

	def __init__(self):
		super().__init__()
		self.__config()

	# config 
	def __config(self):
		cfg = configparser.ConfigParser()

		# read config file
		cfg.read(CONFIG_FILE)

		# set recycle data
		self.alias_url = "http://" + cfg["kibana"]["domain"] + "/"
		self.headers = {"kbn-xsrf": "true"} # must send to kibana 

	############################
	#  ちょっとしたparser
	def _parse_url(self, url):
		if url.startswith("/"):
			return url[1:] # 先頭の/を外す
		else:
			return

	###################
	# Get Method
	def get(self, _url, params=""):
		headers = self.headers
		data = None

		p = parse.urlencode(params)
		url = self.alias_url + _url + "?" + p

		print(url)
		LOG.debug(url)

		# request to REST API
		try:
			req = request.Request(url=url, headers=self.headers, method="GET")
			with request.urlopen(req) as res:
				data = json.loads( res.read() )

		except Exception as e:
			print("---KibanaAPI GET Error---")
			print(e)

		finally:
			return data

	####################
	# POST Method
	# data's type bytes
	def post(self, url, data):
		headers = self.headers
		headers["Content-Type"] = "application/json"
		
		url = self.alias_url+url

		print(url)

		print(data.encode())

		try:
			req = request.Request(url=url, data=data.encode(), headers=headers, method="POST" )
			res = request.urlopen(req)
			print( json.loads( res.read() ) )
		except Exception as e:
			print("---KibanaAPI POST Error---")
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
			print("---KibanaAPI PUT Error---")
			print(e)
		finally:
			pass
		

	########
	# Create multi Objects
	# data = [ {objects},{objects} ]
	def bulk_create_objects(self, data):
		headers = self.headers
		headers["Content-Type"] = "application/json"

		url = self.alias_url + "api/saved_objects/_bulk_create"

		req = request.Request(url=url, data=data.encode(), headers=headers, method="POST")
		with request.urlopen(req) as res:
			print( json.loads( res.read() ) )

class ElasticAPI(object):
	def __init__(self):
		super().__init__()
		self.__config()

	def __config(self):
		cfg = configparser.ConfigParser()

		# read config file
		cfg.read(CONFIG_FILE)

		# set recycle data
		self.alias_url = "http://" + cfg["elastic"]["domain"] + "/"
		self.headers = {"kbn-xsrf": "true"} # must send to kibana 

	###################
	# Get Method
	def get(self, _url, params=""):
		headers = self.headers
		data = None

		p = parse.urlencode(params)
		url = self.alias_url + _url + "?" + p

		LOG.debug(url)

		# request to REST API
		try:
			req = request.Request(url=url, headers=self.headers, method="GET")
			with request.urlopen(req) as res:
				data = json.loads( res.read() )

		except Exception as e:
			print(e)

		finally:

			return data

	def put(self, _url):
		pass	

	#################################
	# get db's fields data types
	def get_db_mapping(self, dbname):
		url = dbname + "/_mapping"
		params = {"pretty":"true"}

		# get data from elsaticsearch 
		data = self.get(url, params)

		return data[dbname]["mappings"]["doc"]["properties"]


#############################
# main 
# test code
if __name__=="__main__":
	bulk_test = []

	ig = IndexPatternGenerator()
	vg = VisualizationGenerator()
	dg = DashboardGenerator()
	ka = KibanaAPI()
	ea = ElasticAPI()

	mappings = ea.get_db_mapping("simulation_20190306_b_without_p240_v9_25km")
	#print("mappings : " + str( type(mappings) ) )
	#print( mappings )

	test_vid =  "test_vid20190325"
	test_iid =  "test_iid20190325"

	#ig_data = ig.genarate("index_test*", mappings, False, test_iid)
	vg_data = vg.genarate(test_vid, ["distance_B_without_p240_v9_25km"], test_iid)

	bulk_test.append( vg.genarate(test_vid, ["distance_B_without_p240_v9_25km"], test_iid, True, test_vid) )


	#print(vg_data)

	print("POST")
	#ka.post(ig.alias + test_iid , ig_data)
	ka.post(vg.alias + test_vid , vg_data)

	print("visualization PUT")
	ka.put(vg.alias + test_vid , vg_data)

	#print("PUT")
	#ka.put(ig.alias + "test_id2222222222222" , ig_data)

	print("get")

	print( ka.get( vg.alias + test_vid ) )
	print( ka.get( vg.alias + "9676cbd0-4ed1-11e9-bdc2-456db92dfbc2" ) )

	#print( ka.get( ig.alias+"test_id20190313") )

	print("bulk_test")
	#ka.bulk_create_objects(json.dumps( bulk_test) )

