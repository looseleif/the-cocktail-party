from flask import Flask, request, jsonify
from threading import Lock
from llama_cpp import Llama
import random

manager_app = Flask(__name__)

LLAMACPP_MODEL_PATH = "./llama-3.2-3b-instruct.Q8_0.gguf"
llamacpp_model = Llama(model_path=LLAMACPP_MODEL_PATH)

lock = Lock()
game_state = {
    "matter_of_fact": [],
    "story": "",
    "secrets": {},
    "players": {},
    "agents": {},
    "conversations": []
}

def build_dynamics(attributes):
    return {
        "happiness": round(attributes["happiness"], 1),
        "hunger": round(attributes["hunger"], 1),
        "attentiveness": round(attributes["attentiveness"], 1),
        "defensiveness": round(attributes["defensiveness"], 1),
        "curiosity": round(attributes["curiosity"], 1)
    }

@manager_app.route("/initialize_state", methods=["POST"])
def initialize_state():
    data = request.json
    with lock:
        game_state["matter_of_fact"] = data.get("matter_of_fact", [])
        game_state["story"] = data.get("story", "")
        game_state["secrets"] = {
            f"secret_{i}": secret for i, secret in enumerate(data.get("secrets", []))
        }

        players = data.get("players", [])
        if players:
            game_state["players"] = {player["player_id"]: player for player in players}

        agents = data.get("agents", [])
        if agents:
            game_state["agents"] = {
                agent["agent_id"]: {
                    "name": agent["name"],
                    "dynamics": [agent["dynamics"]],
                    "backstory": agent.get("backstory", ""),
                    "secret": game_state["secrets"].get(f"secret_{i}", "No secret assigned")  # Add this line
                }
                for i, agent in enumerate(agents)
            }

        
        if len(game_state["matter_of_fact"]) < 2:
            return jsonify({"error": "Not enough facts to generate story and secrets."}), 400
        if not game_state["story"]:
            return jsonify({"error": "Story is missing."}), 400
        if not game_state["players"]:
            return jsonify({"error": "Players are missing."}), 400
        if not game_state["agents"]:
            return jsonify({"error": "Agents are missing."}), 400

    return jsonify({"message": "Game state initialized successfully."}), 200

@manager_app.route("/talk_to_agent", methods=["POST"])
def talk_to_agent():
    data = request.json
    agent_id = data.get("agent_id")
    player_id = data.get("player_id")
    user_input = data.get("input")
    with lock:
        if agent_id not in game_state["agents"]:
            return jsonify({"error": "Agent not found"}), 404
        if player_id not in game_state["players"]:
            return jsonify({"error": "Player not found"}), 404
        
        agent = game_state["agents"][agent_id]
        agent_attributes = agent["dynamics"][-1]

        prompt = agent["name"]
        secret = agent["secret"]
        story_context = game_state.get("story", "")
        facts = '; '.join(game_state.get("matter_of_fact", []))
        full_prompt = (
            f"{prompt}\n"
            f"Story Context: {story_context}\n"
            f"Facts: {facts}\n"
            f"Agent Dynamics: {build_dynamics(agent_attributes)}\n"
            f"Secret: {secret}\n"
            f"User: {user_input}\n"
            f"Agent:"
        )

    response = llamacpp_model(full_prompt)
    
    print(f"Raw Response: {response}")

    
    # Extract the text from the response
    response_text = (
        response.get("choices")[0].get("text").strip()
        if "choices" in response and len(response["choices"]) > 0
        else "No response generated."
    )

    # Print the response text to the console
    print(f"Agent Response: {response_text}")
    
    new_agent_attributes = {k: max(0, min(1, v + random.uniform(-0.1, 0.1))) for k, v in agent_attributes.items()}

    with lock:
        game_state["agents"][agent_id]["dynamics"].append(new_agent_attributes)
        game_state["conversations"].append({
            "index": len(game_state["conversations"]),
            "agent_id": agent_id,
            "player_id": player_id,
            "input": user_input,
            "response": response,
            "agent_dynamics": new_agent_attributes
        })

    return jsonify({
        "response": response,
        "agent_dynamics": new_agent_attributes
    }), 200

if __name__ == "__main__":
    manager_app.run(host="0.0.0.0", port=5555)


# curl -X POST http://localhost:5555/initialize_state \
# -H "Content-Type: application/json" \
# -d @context.json