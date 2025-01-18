import outlines

# Load the model
model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

# Define the three classification options
options = ["Casual Conversation", "Questioning", "Influencing"]

# Define the classification prompt with examples
prompt_template = """You are a conversational assistant trained to classify the nature of user interactions.

Please determine whether the last player input falls into one of the following categories:

- "Casual Conversation": The player is engaging in friendly, informal discussion without a specific intent.
- "Questioning": The player is asking a question to gain information or clarify something.
- "Influencing": The player is attempting to persuade or convey a specific belief, opinion, or unit of information.

# Examples

Player Input: "Hey, how are you doing today?"
Classification: Casual Conversation

Player Input: "What is the capital of France?"
Classification: Questioning

Player Input: "You know, I think the solution to this problem is to use renewable energy."
Classification: Influencing

Player Input: {{ player_input }}
Classification:
"""

# Function to classify player input
def classify_interaction(player_input):
    """Classify the player's input into one of three categories: Casual Conversation, Questioning, or Influencing."""
    try:
        prompt = prompt_template.replace("{{ player_input }}", player_input)
        generator = outlines.generate.choice(model, options)
        classification = generator(prompt).strip()
        return classification
    except Exception as e:
        print(f"Classification failed: {e}")
        return None

# Example conversations
conversations = {
    "Conversation 1": [
        "How was your weekend?",
        "What do you think about the latest movie in that series?",
        "I think we should consider a different strategy for marketing."
    ],
    "Conversation 2": [
        "Did you hear about the new policy changes at work?",
        "What’s your opinion on artificial intelligence ethics?",
        "We need to focus more on sustainability in our decisions."
    ],
    "Conversation 3": [
        "Hey, do you want to grab a coffee later?",
        "What time is the meeting scheduled for tomorrow?",
        "I believe we can achieve better results by collaborating more closely."
    ]
}

# Main script to process conversations
if __name__ == "__main__":
    for convo_name, player_inputs in conversations.items():
        print(f"Processing {convo_name}...\n")
        for player_input in player_inputs:
            result = classify_interaction(player_input)
            print(f"Player Input: {player_input}\nClassification: {result}\n")
        print("-" * 50)
