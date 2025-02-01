from flask import Flask, request, jsonify
from outlines import models, generate
from llama_cpp import Llama

# Define the Flask app
app = Flask(__name__)

# Load the local gguf model
try:
    # Pointing to the llama-3.2 gguf file in the local directory
    llm = Llama("./llama-3.2-3b-instruct.Q8_0.gguf")
    model = models.LlamaCpp(llm)
    generator = generate.choice(model, ["Agree", "Mixed", "Disagree"])
    print("Local model and generator loaded successfully.")
except Exception as e:
    print(f"Model loading failed: {e}")

def evaluate_agreement(conversations, target_statement):
    """
    Evaluate the level of agreement with the target statement in multi-participant conversations.
    """
    participants = set()
    agreement_count = 0
    disagreement_count = 0
    mixed_count = 0
    conversation_count = 0

    try:
        for convo in conversations:
            participants_in_convo = set()
            for message in convo["messages"]:
                participants_in_convo.add(message["sender"])

            participants.update(participants_in_convo)
            conversation_text = "\n".join([
                f"{message['sender']}: {message['content']} ({message['timestamp']})"
                for message in convo["messages"]
            ])

            prompt = f"""
            Does the following multi-participant conversation agree, disagree, or exhibit mixed alignment with the target statement?

            Target Statement: "{target_statement}"
            Conversation:
            {conversation_text}
            """

            try:
                response = generator(prompt).strip()
                print(f"Conversation among participants {', '.join(participants_in_convo)}:\n{response}")

                if response == "Agree":
                    agreement_count += 1
                elif response == "Disagree":
                    disagreement_count += 1
                elif response == "Mixed":
                    mixed_count += 1
                conversation_count += 1
            except Exception as e:
                print(f"Error during model execution: {e}")
                raise

        total_conversations = conversation_count
        return {
            "total_conversations": total_conversations,
            "total_participants": len(participants),
            "agreements": agreement_count,
            "disagreements": disagreement_count,
            "mixed_alignments": mixed_count,
            "agreement_percentage": (agreement_count / total_conversations) * 100 if total_conversations > 0 else 0,
            "disagreement_percentage": (disagreement_count / total_conversations) * 100 if total_conversations > 0 else 0,
            "mixed_percentage": (mixed_count / total_conversations) * 100 if total_conversations > 0 else 0
        }
    except Exception as e:
        print(f"Error in evaluate_agreement: {e}")
        raise

@app.route('/process', methods=['POST'])
def process_conversations():
    """
    Endpoint to process conversations JSON data.
    """
    try:
        data = request.json
        if "conversations" not in data:
            return jsonify({"error": "Invalid data format"}), 400

        target_statement = "The novel \"Animal Farm\" is mentioned in these conversations"
        metrics = evaluate_agreement(data["conversations"], target_statement)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

