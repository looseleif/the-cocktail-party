from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QProgressBar,
    QTextEdit, QWidget, QComboBox, QGroupBox, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt
import json
import requests
import random
import os

# Define the API URLs
INITIALIZE_URL = "http://172.23.101.158:5555/initialize_state"
TALK_URL = "http://172.23.101.158:5555/talk_to_agent"

# Get all JSON files in the active directory
def get_json_files():
    return [file for file in os.listdir() if file.endswith(".json")]

# Load characters from a JSON file
def load_characters(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

# Initialize game state
def initialize_game(context_file):
    characters = load_characters(context_file)
    for agent in characters["agents"]:
        # Add randomness to dynamics
        agent["dynamics"] = {
            "happiness": round(random.uniform(0.5, 1.0), 2),
            "hunger": round(random.uniform(0.1, 0.5), 2),
            "attentiveness": round(random.uniform(0.4, 0.9), 2),
            "defensiveness": round(random.uniform(0.3, 0.7), 2),
            "curiosity": round(random.uniform(0.6, 1.0), 2),
        }

    response = requests.post(INITIALIZE_URL, json=characters)
    if response.status_code == 200:
        window.log_message("Game state initialized successfully!")
        window.update_ascii_table(characters)
        window.display_matter_of_fact(characters["matter_of_fact"])
        window.populate_agent_selector(characters["agents"])
    else:
        window.log_message("Failed to initialize game state.")

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent Interaction")
        self.setGeometry(200, 200, 800, 800)

        # Main layout
        main_layout = QVBoxLayout()

        # Context Selector
        self.context_label = QLabel("Select Context:")
        main_layout.addWidget(self.context_label)

        self.context_selector = QComboBox()
        self.context_selector.addItems(get_json_files())
        main_layout.addWidget(self.context_selector)

        # Initialize Game Button
        self.init_button = QPushButton("Initialize Game State")
        self.init_button.clicked.connect(lambda: initialize_game(self.context_selector.currentText()))
        main_layout.addWidget(self.init_button)

        # Agent Selector
        self.agent_selector_label = QLabel("Select Agent:")
        main_layout.addWidget(self.agent_selector_label)

        self.agent_selector = QComboBox()
        self.agent_selector.currentTextChanged.connect(self.update_selected_agent_dynamics)
        main_layout.addWidget(self.agent_selector)

        # Matter of Fact
        self.matter_label = QLabel("Matter of Fact:")
        main_layout.addWidget(self.matter_label)

        self.matter_display = QTextEdit()
        self.matter_display.setReadOnly(True)
        main_layout.addWidget(self.matter_display)

        # ASCII Table
        self.ascii_table_label = QLabel("Players and Agents:")
        main_layout.addWidget(self.ascii_table_label)

        self.ascii_table = QTextEdit()
        self.ascii_table.setReadOnly(True)
        main_layout.addWidget(self.ascii_table)

        # Input Section
        self.input_label = QLabel("Enter your message:")
        main_layout.addWidget(self.input_label)

        self.message_input = QTextEdit()
        main_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Talk to Agent")
        self.send_button.clicked.connect(self.talk_to_agent)
        main_layout.addWidget(self.send_button)

        # Response
        self.response_label = QLabel("Agent Response:")
        main_layout.addWidget(self.response_label)

        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        main_layout.addWidget(self.response_display)

        # Dynamics Section
        self.dynamics_group = QGroupBox("Agent Dynamics")
        self.dynamics_layout = QVBoxLayout()
        self.dynamics_group.setLayout(self.dynamics_layout)
        main_layout.addWidget(self.dynamics_group)

        # Set the layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def log_message(self, message):
        self.response_display.append(message)

    def display_matter_of_fact(self, matter_of_fact):
        self.matter_display.clear()
        for fact in matter_of_fact:
            self.matter_display.append(f"- {fact}")

    def update_ascii_table(self, character_data):
        self.ascii_table.clear()
        self.ascii_table.append("Player & Agent Table:\n")
        self.ascii_table.append("=" * 40)
        for player in character_data["players"]:
            self.ascii_table.append(f"{player['name']} ({player['role']})")
        for agent in character_data["agents"]:
            self.ascii_table.append(f"{agent['name']} (Agent)")
        self.ascii_table.append("=" * 40)

    def populate_agent_selector(self, agents):
        self.agent_selector.clear()
        for agent in agents:
            self.agent_selector.addItem(agent["name"], agent)

    def update_selected_agent_dynamics(self):
        selected_agent = self.agent_selector.currentData()
        if selected_agent:
            self.display_agent_dynamics(selected_agent)

    def display_agent_dynamics(self, agent):
        # Clear existing dynamics
        for i in reversed(range(self.dynamics_layout.count())):
            self.dynamics_layout.itemAt(i).widget().setParent(None)

        # Add dynamics progress bars
        for dynamic, value in agent["dynamics"].items():
            label = QLabel(f"{dynamic.capitalize()}: {value * 100:.0f}%")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(value * 100))
            self.dynamics_layout.addWidget(label)
            self.dynamics_layout.addWidget(bar)

    def talk_to_agent(self):
        selected_agent = self.agent_selector.currentData()
        if not selected_agent:
            self.log_message("Please select an agent to talk to.")
            return

        agent_id = selected_agent["agent_id"]
        player_id = "player1"
        user_input = self.message_input.toPlainText().strip()

        if not user_input:
            self.log_message("Please enter a message to talk to the agent.")
            return

        # Prepare payload
        payload = {
            "agent_id": agent_id,
            "player_id": player_id,
            "input": user_input
        }

        self.log_message(f"Sending payload: {payload}")

        try:
            response = requests.post(TALK_URL, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()

            self.log_message(f"Response from server: {data}")

            if "response" in data:
                self.log_message(f"Agent: {data['response']}")

            if "agent_dynamics" in data:
                self.display_agent_dynamics(data["agent_dynamics"])
            else:
                self.log_message("No dynamics data provided for the agent.")
        except requests.exceptions.RequestException as e:
            self.log_message(f"Error communicating with the agent: {e}")

# Start the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
