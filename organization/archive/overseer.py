from flask import Flask, request, jsonify

app = Flask(__name__)

game_states = {}

@app.route("/generate_state", methods=["POST"])
def generate_state():
    data = request.json
    context = data.get("context")
    facts = data.get("facts")
    agents = data.get("agents")
    secrets = data.get("secrets")

    if not context or not facts or not agents:
        return jsonify({"error": "Incomplete data provided"}), 400

    state_id = f"state_{len(game_states) + 1}"
    game_states[state_id] = {
        "context": context,
        "facts": facts,
        "agents": agents,
        "secrets": secrets
    }

    return jsonify({
        "message": "Game state generated successfully",
        "state_id": state_id,
        "context": context,
        "facts": facts,
        "agents": agents,
        "secrets": secrets
    }), 200

@app.route("/get_state/<state_id>", methods=["GET"])
def get_state(state_id):
    if state_id not in game_states:
        return jsonify({"error": "State not found"}), 404

    return jsonify(game_states[state_id]), 200

@app.route("/update_state/<state_id>", methods=["POST"])
def update_state(state_id):
    if state_id not in game_states:
        return jsonify({"error": "State not found"}), 404

    data = request.json
    if "context" in data:
        game_states[state_id]["context"] = data["context"]
    if "facts" in data:
        game_states[state_id]["facts"] = data["facts"]
    if "agents" in data:
        game_states[state_id]["agents"] = data["agents"]
    if "secrets" in data:
        game_states[state_id]["secrets"] = data["secrets"]

    return jsonify({"message": "Game state updated successfully"}), 200

@app.route("/delete_state/<state_id>", methods=["DELETE"])
def delete_state(state_id):
    if state_id not in game_states:
        return jsonify({"error": "State not found"}), 404

    del game_states[state_id]
    return jsonify({"message": "Game state deleted successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4545)
