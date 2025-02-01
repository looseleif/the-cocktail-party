import requests

# Define the API URL
API_URL = "http://localhost:5555/initialize_state"

# Character data to send in the request
character_data = {
    "matter_of_fact": [
        "The kingdom is under threat from a mysterious force.",
        "The ancient artifact holds the key to salvation."
    ],
    "story": "In a distant land, heroes gather to uncover hidden truths and protect their home.",
    "secrets": [
        "The artifact is cursed.",
        "One of the heroes is a traitor."
    ],
    "players": [
        {
            "player_id": "player1",
            "name": "Hero1",
            "role": "warrior"
        }
    ],
    "agents": [
        {
            "agent_id": "agent1",
            "name": "Guardian",
            "dynamics": {
                "happiness": 0.8,
                "hunger": 0.2,
                "attentiveness": 0.9,
                "defensiveness": 0.5,
                "curiosity": 0.7
            },
            "backstory": "A loyal protector of the ancient artifact."
        }
    ]
}

# Send POST request to initialize the game state
response = requests.post(API_URL, json=character_data)

# Print the response
if response.status_code == 200:
    print("Character created successfully:")
    print(response.json())
else:
    print("Failed to create character. Error:")
    print(response.json())

