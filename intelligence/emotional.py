import outlines
from outlines.samplers import greedy
from enum import Enum
from pydantic import BaseModel

model = outlines.models.transformers("TheBloke/Mistral-7B-OpenOrca-AWQ", device="cuda")

@outlines.prompt
def emotion_classifier(text):
    """You are a highly empathetic assistant trained to understand emotions.

    Given a piece of text, classify the overall emotion as either "HAPPY" or "SAD".

    # Examples

    Text: "I just got promoted at work!"
    Label: HAPPY

    Text: "I feel so lonely right now."
    Label: SAD

    # TASK

    Text: {{ text }}
    Label: """

generator = outlines.generate.choice(model, ["HAPPY", "SAD"], sampler=greedy())

texts = [
    "I love spending time with my family during the holidays!",
    "It's been such a tough year, and I feel like giving up.",
    "Today has been amazing! I got to see my best friend after years.",
    "I just lost my wallet and can't find it anywhere.",
    "The sunshine makes me feel so alive and happy!",
    "I miss my childhood days so much, it makes me cry sometimes.",
    "I received the best surprise gift from my partner today!",
    "I failed my exam even though I studied so hard.",
    "It's my birthday, and all my friends came to celebrate with me!",
    "I feel so isolated and disconnected from everyone.",
    "We won the championship game! It feels incredible!",
    "My pet has been sick for days, and I am so worried.",
    "My new job has been so fulfilling and exciting!",
    "I got stuck in traffic for hours and missed my appointment.",
    "I just finished a great workout and feel so energized!",
    "My best friend moved away, and I feel so lonely now."
]

prompts = [emotion_classifier(text) for text in texts]

labels = generator(prompts)
print("Labels using generate.choice:", labels)

class EmotionLabel(str, Enum):
    happy = "HAPPY"
    sad = "SAD"

class EmotionClassification(BaseModel):
    label: EmotionLabel

generator_json = outlines.generate.json(model, EmotionClassification, sampler=greedy())

labels_json = generator_json(prompts)
print("Labels using generate.json:", labels_json)
