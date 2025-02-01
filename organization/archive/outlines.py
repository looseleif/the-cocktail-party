from flask import Flask, request, jsonify
from llama_cpp import Llama

# Initialize Flask app
app = Flask(__name__)

# Path to the Mistral model
MODEL_PATH = "./mistral-7b-instruct-v0.2.Q5_K_M.gguf"

# Load the Mistral model
print("Loading the model...")
model = Llama(model_path=MODEL_PATH)
print("Model loaded successfully.")

@app.route("/process", methods=["POST"])
def process_conversations():
    """
    Endpoint to process conversations and extract structured information.
    """
    try:
        # Get JSON data from the request
        data = request.json
        conversations = data.get("conversations", "")

        # Construct the prompt for the model
        prompt = (
            "Analyze the following conversations and extract factual information:\n\n"
            f"{conversations}\n\n"
        )

        # Generate a response using the Mistral model
        response = model(prompt, max_tokens=50)
        try:
            output = response["choices"][0]["text"].strip()
        except (KeyError, IndexError):
            return jsonify({"error": "Unexpected response format from the model"}), 500

        return jsonify({"facts": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run the Flask server

