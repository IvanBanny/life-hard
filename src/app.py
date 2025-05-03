from flask import Flask
import os

app = Flask(__name__, static_folder="static", static_url_path="")
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.secret_key = "dasfasgsdfgdfsaafdadfadsfdadsfsa"
