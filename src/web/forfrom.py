import os,sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)

print(parentdir)
sys.path.insert(0,parentdir)

from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import resas_elastic
from util import csv_output
import cgi

ra = resas_elastic.ResasAPI()
app = Flask(__name__)

#res = request.get('http://127.0.0.1:8080')
#res.raise_for_status()
#soup = bs4.BeautifulSoup(res.text, "html.parser")
#print(soup.title)
"""
@app.route('/index')
def index():
	return  render_template('index.html')

"""
@app.route('/form')
def form():

	return render_template('form.html')

def main():
	app.debug = True
	app.run(host='127.0.0.1', port=8080)


@app.route('/forfrom', methods = ['POST', 'GET'])
def forfrom():
	ra = resas_elastic.ResasAPI()
	data = None
	if request.method == 'POST':
		print(request)
		my_dic = request.form
		print(my_dic)
		data = ra.forFrom(my_dic['key'],my_dic['prefcode'],my_dic['purpose'])
	return str(data)


if __name__ == "__main__":
	main()
