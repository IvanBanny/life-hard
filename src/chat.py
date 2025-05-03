from flask import jsonify, session

from .app import app
from .llm_utils import generate_response
from .bunq_utils import get_budget

@app.route('/api/chat', methods=['GET'])
def generate_itinerary():
    """Chat with the LLM to generate a travel itinerary."""
    if "form_data" not in session:
        return jsonify({"error": "Form data not found"}), 400
    
    try:
        if getattr(session, "changed", False) or session.get("response") is None:
            session.changed = False  # Reset the changed flag
            prompt = f"I have {session['budget']} for traveling. I want to travel to {session['form_data']['country']} in the dates of {session['form_data']['dates']}. Please create a very very very short itinerary."
            response = generate_response(prompt)

            if response:
                session["response"] = response  # Cache the response in the session
            else:
                return jsonify({"error": "Failed to generate itinerary"}), 500
        
        return jsonify({"response": session["response"]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
