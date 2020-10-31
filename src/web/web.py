import os,sys
import json
import pandas as pd

currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)

print(parentdir)
sys.path.insert(0,parentdir)

from flask import Flask, render_template, request, Response, make_response
import resas_elastic
from util import csv_output
from tools import estool


ra = resas_elastic.ResasAPI()
rv = csv_output.ResasCSV()
et = estool.Estool()

app = Flask(__name__)

############################################################
##レスポンスヘッダの拡張
############################################################
def prepare_response(data):
	response = make_response(data)
	response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
	response.headers['X-Content-Type-Options'] = 'nosniff'
	response.headers['X-Frame-Options'] = 'SAMEORIGIN'
	response.headers['X-XSS-Protection'] = '1; mode=block'
	return response

@app.route('/home')
def home():
	return render_template('home.html')

@app.route("/data/bar")
def data_bar():
	return render_template('tes.html')

@app.route("/data")
def data():
	return render_template('test1.html')

@app.route('/employ_form')
def employ_form():
	return render_template('employ_form.html')

@app.route('/commute_form')
def commute_form():
	return render_template('commute_form.html')

@app.route('/forfrom_form')
def forfrom_form():
	return render_template('forfrom_form.html')

@app.route('/population_form')
def population_form():
	return render_template('population_form.html')


"""
@app.route('/employ', methods = ['POST', 'GET'])
def employ():
	ra = resas_elastic.ResasAPI()
	data = None
	if request.method == 'POST':
		my_dic = request.form
		data = ra.employ(my_dic['prefcode'],my_dic['dMethod'],my_dic['matter'],my_dic['classifi'],my_dic['dType'],my_dic['gender'])
	rv.insert_es("test1",data)
	response_body = render_template('result.html', message=data)
	response = prepare_response(response_body)
	return response
"""

@app.route('/population', methods = ['POST', 'GET'])
def population():
	ra = resas_elastic.ResasAPI()
	data = None
	if request.method == 'POST':
		my_dic = request.form
		data = ra.population(
			my_dic['prefCode'],
			my_dic['cityCode'],
			)
	#rv.insert_es("population",data)
	#response_body = render_template('result.html', message=data)
	response_body = render_template('result.html', message=data)
	response = prepare_response(response_body)
	return response


############################
# 指定地域への国籍別訪問者数 2011.2q ~ 2016 3q
# term 2011 ~ 2016
# prefcode 27:Osaka 都道府県
# purpose 1:all or 2: only leisure, Sightseeing
#

##forfromのデータを
@app.route('/forfrom', methods = ['POST', 'GET'])
def forfrom():
	ra = resas_elastic.ResasAPI()
	data = None
	if request.method == 'POST':
		my_dic = request.form
		data = ra.forFrom(my_dic['term'],my_dic['prefCode'],my_dic['purpose'])
	##rv.insert_es("test1",data)
	response_body = render_template('result.html', message=data)
	response = prepare_response(response_body)
	return response

@app.route('/commute', methods = ['POST', 'GET'])
def commute():
	ra = resas_elastic.ResasAPI()
	data = None
	if request.method == 'POST':
		my_dic = request.form
		data = ra.commute(my_dic['mode'],my_dic['year'],my_dic['prefCode'],my_dic['cityCode'])
	##rv.insert_es("test1",data)
	response_body = render_template('tes.html', message=data)
	response = prepare_response(response_body)
	return response

##########
# デモ用

@app.route('/demo')
def demo():
	dbname = "population"
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
	data = et.get_query(dbname, query)
	#data2 = et.get_query("population_fluctuation", query)

	return render_template('demo.html', data=data)#, data2=data2)

@app.route('/demo2')
def demo2():

	dbname = "population"
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
	data = et.get_query(dbname, query)
	data2 = et.get_query("population_fluctuation", query)

	return render_template('demo2.html', data=data, data2=data2)

@app.route('/es_search')
def es_search():
	est = estool.Estool()
	index = est.get_index()
	print(index)
	return render_template('es_search.html', index=index)

@app.route('/demo3')
def demo3():
	data2 = [];
	dbname = "population"
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
	data = et.get_query(dbname, query)
	#data2 = et.get_query("population_fluctuation", query)

	return render_template('demo3.html', data=data)#, data2=data2)

@app.route('/demo4')
def demo4():
	return render_template('demo4.html')

@app.route('/demo/getData')
def demo_getData():
	pass

###
# Main function
#
def main():
	app.debug = True
	app.run(host='127.0.0.1', port=8080)


if __name__ == "__main__":
	main()
