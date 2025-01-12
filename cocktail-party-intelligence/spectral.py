import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def emotion_rater(context, emotion):
    """You are a conversational assistant trained to evaluate interactions.

    Please determine the updated {emotion} level for the agent, which should be within 1 or 2 points up or down
    from its current value. The updated value must always be between 0 and 10.

    # Examples

    Conversation: ["Hey, I just wanted to say thank you for helping me yesterday!", "No problem, happy to help!", "You're the best!"]
    Current {emotion.capitalize()} Level: 5
    Updated {emotion.capitalize()} Level: 7

    Conversation: ["I'm feeling really down today and nothing seems to go right.", "I'm sorry to hear that. Is there anything I can do?", "No, I just need some time."]
    Current {emotion.capitalize()} Level: 6
    Updated {emotion.capitalize()} Level: 4

    # TASK

    Conversation: {{ context }}
    """

def get_emotion_values(context):
    emotions = ["happiness", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation", "boredom", "curiosity"]
    updated_emotions = {}

    for emotion in emotions:
        try:
            prompt = emotion_rater(context=context, emotion=emotion)
            updated_level = outlines.generate.format(model, int)(prompt)
            updated_emotions[emotion] = max(0, min(10, updated_level))
        except Exception as e:
            print(f"{emotion.capitalize()} rating failed: {e}")

    return updated_emotions