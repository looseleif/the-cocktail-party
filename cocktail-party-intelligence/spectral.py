import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def emotion_rater(conversation, emotion):
    """You are a conversational assistant trained to evaluate interactions.

    Please determine the change in {emotion} level that
    the agent will have considering you can evaluate a number between -5 and 5.

    # Examples

    Conversation: ["Hey, I just wanted to say thank you for helping me yesterday!", "No problem, happy to help!", "You're the best!"]
    {emotion.capitalize()} Change: 3

    Conversation: ["I'm feeling really down today and nothing seems to go right.", "I'm sorry to hear that. Is there anything I can do?", "No, I just need some time."]
    {emotion.capitalize()} Change: -2

    # TASK

    Conversation: {{ conversation }}
    {emotion.capitalize()} Change: """


def get_emotion_change(conversation):
    emotions = ["happiness", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation", "boredom", "curiosity"]
    emotion_changes = {}

    for emotion in emotions:
        try:
            prompt = emotion_rater(conversation=conversation, emotion=emotion)
            emotion_change = outlines.generate.format(model, int)(prompt)
            emotion_changes[emotion] = emotion_change
        except Exception as e:
            print(f"{emotion.capitalize()} rating failed: {e}")
            emotion_changes[emotion] = 0  # Default value for the emotion change

    return emotion_changes
