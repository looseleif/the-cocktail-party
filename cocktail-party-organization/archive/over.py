from flask import Flask, request, jsonify
import outlines
from pydantic import BaseModel, constr
from enum import Enum

# Define RPG models
class Weapon(str, Enum):
    sword = "sword"
    axe = "axe"
    mace = "mace"
    spear = "spear"
    bow = "bow"
    crossbow = "crossbow"

class Armor(str, Enum):
    leather = "leather"
    chainmail = "chainmail"
    plate = "plate"

class Character(BaseModel):
    name: constr(max_length=10)
    age: int
    armor: Armor
    weapon: Weapon
    strength: int

# Initialize the Outlines model
model = outlines.models.llamacpp("./mistral-7b-instruct-v0.2.Q5_K_M.gguf")
generator = outlines.generate.json(model, Character)

# Initialize Flask app
app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_character():
    data = request.json
    prompt = data.get("prompt", "")
    seed = data.get("seed", 1234)

    sequence = generator(prompt, seed=seed, max_tokens=512)
    return jsonify(sequence)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
