import tkinter as tk
from tkinter import messagebox
import requests

# Define the API URLs
INITIALIZE_URL = "http://localhost:5555/initialize_state"
TALK_URL = "http://localhost:5555/talk_to_agent"

# Initialize game state
def initialize_game():
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

    response = requests.post(INITIALIZE_URL, json=character_data)
    if response.status_code == 200:
        messagebox.showinfo("Success", "Game state initialized successfully!")
    else:
        messagebox.showerror("Error", "Failed to initialize game state.")

# Talk to agent function
def talk_to_agent():
    agent_id = "agent1"
    player_id = "player1"
    user_input = input_entry.get()

    if not user_input.strip():
        messagebox.showwarning("Input Error", "Please enter some text to talk to the agent.")
        return

    payload = {
        "agent_id": agent_id,
        "player_id": player_id,
        "input": user_input
    }

    response = requests.post(TALK_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        response_label.config(text=f"Agent: {data['response']}")
        dynamics_label.config(
            text=f"Dynamics: {data['agent_dynamics']}\nHappiness: {data['happiness']}"
        )
    else:
        messagebox.showerror("Error", "Failed to communicate with the agent.")

# Create the main GUI window
root = tk.Tk()
root.title("Agent Interaction")

# Input and buttons
input_label = tk.Label(root, text="Enter your message:")
input_label.pack(pady=5)

input_entry = tk.Entry(root, width=50)
input_entry.pack(pady=5)

send_button = tk.Button(root, text="Talk to Agent", command=talk_to_agent)
send_button.pack(pady=10)

response_label = tk.Label(root, text="Agent: [Response will appear here]", wraplength=400, justify="left")
response_label.pack(pady=10)

dynamics_label = tk.Label(root, text="Dynamics: [Dynamics will appear here]", wraplength=400, justify="left")
dynamics_label.pack(pady=10)

# Initialize game button
initialize_button = tk.Button(root, text="Initialize Game State", command=initialize_game)
initialize_button.pack(pady=10)

# Run the GUI event loop
root.mainloop()

