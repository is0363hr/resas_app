import os,sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)

print(parentdir)
sys.path.insert(0,parentdir)

from flask import Flask, render_template, url_for, flash, redirect
app = Flask(__name__)
posts = [
	[11,12,13,14],
	[21,22,23,24],
	[31,32,33,34]
	]
@app.route("/")
def home():
	return render_template('home.html', posts=posts)

if __name__ == '__main__':
	app.run(DEBUG=True)
