import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def happiness_rater(conversation):
    """You are a conversational assistant trained to evaluate interactions.

    Please determine the new happiness level that
    the agent will have after hearing the latest comment from the user based on this context.

    # Examples

    Conversation: "Hey, I just wanted to say thank you for helping me yesterday!"
    Happiness Rating: 9

    Conversation: "I'm feeling really down today and nothing seems to go right."
    Happiness Rating: 2

    # TASK

    Conversation: {{ conversation }}
    Happiness Rating: """

def get_happiness(conversation):
    try:
        prompt = happiness_rater(conversation)
        happiness_rating = outlines.generate.format(model, int)(prompt)
        return happiness_rating
    except Exception as e:
        print(f"Happiness rating failed: {e}")
        return 5  # Default happiness value
