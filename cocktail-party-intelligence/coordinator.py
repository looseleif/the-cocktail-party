import outlines

# Load the model
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

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

# Example usage
if __name__ == "__main__":
    # Example inputs for testing
    examples = [
        "Hey, did you watch the game last night?",
        "Can you tell me how to set up my email account?",
        "I believe climate change is the most urgent issue of our time."
    ]

    for example in examples:
        result = classify_interaction(example)
        print(f"Player Input: {example}\nClassification: {result}\n")
