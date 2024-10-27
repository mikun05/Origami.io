from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_cors import CORS, cross_origin
from dxf_upload.routes import dxf_upload_bp
import os

app = Flask(__name__)
CORS(app)

app.register_blueprint(dxf_upload_bp)

@app.route('/')
@cross_origin()
def home():
    return "ORIGAMI!"


if __name__ == "__main__":
    app.run(debug=True)
