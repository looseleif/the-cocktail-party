import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def attentiveness_rater(conversation):
    """You are an AI evaluator trained to assess the attentiveness of an AI agent in a conversation.

    Given a back-and-forth conversation between a player and an AI agent, rate the AI's attentiveness
    on a scale from 1 to 10, where 1 is very inattentive and 10 is highly attentive.

    # Examples

    Conversation: "Player: Can you help me with my math homework?\nAgent: Sure! What topic are you working on?\nPlayer: It's about algebra.\nAgent: Great! Let's start with the basics."
    Attentiveness Rating: 9

    Conversation: "Player: I'm feeling sad today.\nAgent: Oh, okay.\nPlayer: I just need someone to listen.\nAgent: What else is going on?"
    Attentiveness Rating: 6

    # TASK

    Conversation: {{ conversation }}
    Attentiveness Rating: """

conversations_attentiveness = [
    "Player: Can you tell me a joke?\nAgent: Sure! Why did the scarecrow win an award?\nPlayer: Why?\nAgent: Because he was outstanding in his field!",
    "Player: I need help with a recipe.\nAgent: What recipe are you working on?\nPlayer: A chocolate cake.\nAgent: Do you have all the ingredients ready?",
    "Player: What's the weather like today?\nAgent: It's sunny.\nPlayer: Should I carry an umbrella?\nAgent: Maybe.",
    "Player: I'm so stressed about my project.\nAgent: Tell me more about your project.\nPlayer: It's due tomorrow, and I haven't started.\nAgent: That sounds tough. Let's break it into steps.",
    "Player: I feel like nobody listens to me.\nAgent: I'm here to listen. What's on your mind?\nPlayer: Just a lot of things.\nAgent: Take your time, and we can talk through it."
]

prompts_attentiveness = [attentiveness_rater(conversation) for conversation in conversations_attentiveness]

ratings_attentiveness = [outlines.generate.format(model, int)(prompt) for prompt in prompts_attentiveness]

for conversation, rating in zip(conversations_attentiveness, ratings_attentiveness):
    print(f"Conversation: {conversation}\nAttentiveness Rating: {rating}\n")
