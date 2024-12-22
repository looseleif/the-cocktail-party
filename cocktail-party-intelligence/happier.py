import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def happiness_rater(conversation):
    """You are a conversational assistant trained to evaluate interactions.

    Given a conversation, rate the overall happiness level on a scale from 1 to 10,
    where 1 is very unhappy and 10 is extremely happy.

    # Examples

    Conversation: "Hey, I just wanted to say thank you for helping me yesterday!"
    Happiness Rating: 9

    Conversation: "I'm feeling really down today and nothing seems to go right."
    Happiness Rating: 2

    # TASK

    Conversation: {{ conversation }}
    Happiness Rating: """

conversations = [
    "Hi there! I'm so excited to share my good news with you!",
    "I'm having a really bad day and need someone to talk to.",
    "You always know how to make me smile, thank you!",
    "I just can't seem to catch a break lately...",
    "I'm feeling great today! Everything is going my way!",
    "I feel so overwhelmed and stressed right now.",
    "Thanks for always being there for me, it means a lot.",
    "I'm so tired of everything going wrong."
]

prompts = [happiness_rater(conversation) for conversation in conversations]

ratings = [outlines.generate.format(model, int)(prompt) for prompt in prompts]

for conversation, rating in zip(conversations, ratings):
    print(f"Conversation: {conversation}\nHappiness Rating: {rating}\n")
