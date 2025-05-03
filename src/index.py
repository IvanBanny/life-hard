from flask import session, request, redirect

from .app import app
from .bunq_utils import get_budget

@app.route("/", methods=["GET"])
def index():
    # Update budget value
    if not getattr(session, "changed", False):
        old_budget = session.get("budget")
        session["budget"] = get_budget()
        print(f"Old budget: {old_budget}, New budget: {session['budget']}")
        if old_budget != session["budget"]:
            session.changed = True  # Mark session as changed
            print(f"Budget updated: {session['budget']}")
            return redirect("/form")

    return app.send_static_file("index.html")
