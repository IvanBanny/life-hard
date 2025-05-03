from flask import session, redirect

from .app import app

@app.route("/")
def index():
    if session.get("form_data") is not None:
        return app.send_static_file("index.html")
    return redirect("/form")
