import uuid
from flask import session, g

from .app import app


@app.before_request
def before_request():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        print(f"New session created: {session['user_id']}")
    g.user_id = session["user_id"]

    # Just assign a set sandbox user api key value for now (this value is not confidential)
    session["bunq_api_key"] = "sandbox_7e1f1eb829ede1d3f3e193f3abac11635610b7cabc14f7aa849ca88d"
