import outlines
from outlines.samplers import greedy

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def emotion_rater(conversation, emotion):
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

    Conversation: {{ conversation }}
    Current {emotion.capitalize()} Level: {{ current_level }}
    Updated {emotion.capitalize()} Level: """

def get_emotion_values(conversation, current_dynamics):
    emotions = ["happiness", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation", "boredom", "curiosity"]
    updated_emotions = {}

    for emotion in emotions:
        try:
            current_level = current_dynamics.get(emotion, 5)  # Default to 5 if emotion not in dynamics
            prompt = emotion_rater(conversation=conversation, emotion=emotion, current_level=current_level)
            updated_level = outlines.generate.format(model, int)(prompt)
            updated_emotions[emotion] = max(0, min(10, updated_level))  # Ensure value stays between 0 and 10
        except Exception as e:
            print(f"{emotion.capitalize()} rating failed: {e}")
            updated_emotions[emotion] = current_level  # Retain current level if error occurs

    return updated_emotions