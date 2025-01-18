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

# Example usage
if __name__ == "__main__":
    # Example inputs for testing
    examples = [
        "How was your weekend?",
        "What do you think about the latest movie in that series?",
        "Can you explain how this system works?",
        "The weather has been really nice lately, hasn’t it?",
        "Why did they choose that approach for the project?",
        "I think we should consider a different strategy for marketing.",
        "Did you hear about the new policy changes at work?",
        "What’s your opinion on artificial intelligence ethics?",
        "We need to focus more on sustainability in our decisions.",
        "Hey, do you want to grab a coffee later?",
        "What time is the meeting scheduled for tomorrow?",
        "I suggest we allocate more resources to the development team.",
        "Did you catch the latest episode of that show?",
        "How do you feel about taking on that new responsibility?",
        "The team is doing a great job; we just need to fine-tune the details.",
        "I heard there’s a new restaurant opening downtown. Want to check it out?",
        "Who’s responsible for finalizing the report?",
        "This approach will save us both time and money in the long run.",
        "What’s the best way to get to the event from here?",
        "I believe we can achieve better results by collaborating more closely.",
        "Hey, have you seen my notebook anywhere?",
        "How does this tool compare to the one we used before?",
        "We should re-evaluate our targets based on the latest data.",
        "Are you planning to attend the workshop next week?",
        "I feel like our current process could be more efficient with automation.",
        "Do you know when the project deadline is?",
        "I think adopting a hybrid work model would benefit the team.",
        "What’s your take on the changes in the market?",
        "I heard they’re hiring more people for the development team.",
        "Have you thought about incorporating user feedback into the design?"
    ]


    for example in examples:
        result = classify_interaction(example)
        print(f"Player Input: {example}\nClassification: {result}\n")
