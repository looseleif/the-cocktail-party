from flask import Flask, request, jsonify
from threading import Lock
from llama_cpp import Llama
import random
from spectral import get_emotion_values
import json

manager_app = Flask(__name__)

LLAMACPP_MODEL_PATH = "./llama-3.2-3b-instruct.Q8_0.gguf"
llamacpp_model = Llama(model_path=LLAMACPP_MODEL_PATH)

lock = Lock()

# Game state and active running state
initial_game_state = {
    "matter_of_fact": [],
    "story": "",
    "secrets": {},
    "players": {},
    "agents": {},
    "conversations": []
}

active_game_state = {}  # Active running state

@manager_app.route("/initialize_state", methods=["POST"])
def initialize_state():
    global active_game_state
    data = request.json
    with lock:
        # Initialize game state from input data
        active_game_state = json.loads(json.dumps(initial_game_state))  # Create a deep copy
        active_game_state["matter_of_fact"] = data.get("matter_of_fact", [])
        active_game_state["story"] = data.get("story", "")
        active_game_state["secrets"] = {
            f"secret_{i}": secret for i, secret in enumerate(data.get("secrets", []))
        }

        players = data.get("players", [])
        if players:
            active_game_state["players"] = {player["player_id"]: player for player in players}

        agents = data.get("agents", [])
        if agents:
            active_game_state["agents"] = {
                agent["agent_id"]: {
                    "name": agent["name"],
                    "dynamics": [agent.get("dynamics", {})],  # Use provided dynamics instead of random values
                    "backstory": agent.get("backstory", "")
                }
                for agent in agents
            }

        if len(active_game_state["matter_of_fact"]) < 2:
            return jsonify({"error": "Not enough facts to generate story and secrets."}), 400
        if not active_game_state["story"]:
            return jsonify({"error": "Story is missing."}), 400
        if not active_game_state["players"]:
            return jsonify({"error": "Players are missing."}), 400
        if not active_game_state["agents"]:
            return jsonify({"error": "Agents are missing."}), 400

    return jsonify({"message": "Game state initialized successfully."}), 200

@manager_app.route("/talk_to_agent", methods=["POST"])
def talk_to_agent():
    data = request.json
    agent_id = data.get("agent_id")
    player_id = data.get("player_id")
    user_input = data.get("input")
    with lock:
        if agent_id not in active_game_state["agents"]:
            return jsonify({"error": "Agent not found"}), 404
        if player_id not in active_game_state["players"]:
            return jsonify({"error": "Player not found"}), 404

        agent = active_game_state["agents"][agent_id]
        agent_attributes = agent["dynamics"][-1]

        story_context = active_game_state.get("story", "")
        facts = "; ".join(active_game_state.get("matter_of_fact", []))
        secrets = "; ".join(active_game_state.get("secrets", {}).values())
        
        # Cleaner context output
        full_prompt = (
            f"--- Context for the Agent ---\n"
            f"Story Context:\n{story_context}\n\n"
            f"Facts:\n{facts}\n\n"
            f"Agent Dynamics:\n{json.dumps(agent_attributes, indent=2)}\n\n"
            f"Secrets:\n{secrets}\n\n"
            f"User Input:\n{user_input}\n"
            f"Agent Response:\n"
        )
        
        print(full_prompt)

    response = llamacpp_model(full_prompt)
    response_text = response.get("choices")[0].get("text").strip() if response else "No response generated."
    print(f"Agent Response: {response_text}")

    # Calculate updated emotion values
    updated_emotions = calculate_updated_emotions(agent_attributes, user_input, response_text, story_context, facts, secrets)
    print("\nUpdated Emotions:")
    for emotion, value in updated_emotions.items():
        print(f"{emotion.capitalize()}: {value}")

    # Update dynamics with new values
    new_agent_attributes = {
        emotion: max(0, min(10, value))
        for emotion, value in updated_emotions.items()
    }

    with lock:
        active_game_state["agents"][agent_id]["dynamics"].append(new_agent_attributes)
        active_game_state["conversations"].append({
            "index": len(active_game_state["conversations"]),
            "agent_id": agent_id,
            "player_id": player_id,
            "input": user_input,
            "response": response_text,
            "agent_dynamics": new_agent_attributes
        })

    return jsonify({
        "response": response_text,
        "agent_dynamics": new_agent_attributes
    }), 200


def calculate_updated_emotions(current_dynamics, user_input, agent_response, story_context, facts, secrets):
    """
    Calculate updated emotion values based on the current dynamics, user input, agent response, and additional context.
    Each emotion value is adjusted up or down by 1 or 2 points within the valid range of 0 to 10.
    """
    context = {
        "current_dynamics": current_dynamics,
        "user_input": user_input,
        "agent_response": agent_response,
        "story_context": story_context,
        "facts": facts,
        "secrets": secrets
    }
    print("Emotion context:", json.dumps(context, indent=2))
    
    updated_emotions = {}
    emotions = get_emotion_values(context)
    updated_emotions = emotions
    
    print(updated_emotions)

    return updated_emotions


@manager_app.route("/get_active_state", methods=["GET"])
def get_active_state():
    with lock:
        return jsonify(active_game_state), 200

if __name__ == "__main__":
    manager_app.run(host="0.0.0.0", port=5555)
