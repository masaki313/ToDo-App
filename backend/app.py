from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")
