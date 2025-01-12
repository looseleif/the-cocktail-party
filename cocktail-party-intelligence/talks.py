from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton,
    QTextEdit, QWidget, QComboBox, QGroupBox, QScrollArea, QProgressBar
)
from PyQt5.QtCore import Qt
import requests
import json
import os

# Define the API URLs
INITIALIZE_URL = "http://172.23.101.158:5555/initialize_state"
TALK_URL = "http://172.23.101.158:5555/talk_to_agent"
ACTIVE_STATE_URL = "http://172.23.101.158:5555/get_active_state"

# Get all JSON files in the active directory
def get_json_files():
    return [file for file in os.listdir() if file.endswith(".json")]

# Load characters from a JSON file
def load_characters(file_name):
    with open(file_name, "r") as file:
        return json.load(file)

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game State Viewer and Interaction")
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
        self.init_button.clicked.connect(self.initialize_game)
        main_layout.addWidget(self.init_button)

        # Agent Selector
        self.agent_selector_label = QLabel("Select Agent:")
        main_layout.addWidget(self.agent_selector_label)

        self.agent_selector = QComboBox()
        main_layout.addWidget(self.agent_selector)

        # Matter of Fact
        self.matter_label = QLabel("Matter of Fact:")
        main_layout.addWidget(self.matter_label)

        self.matter_display = QTextEdit()
        self.matter_display.setReadOnly(True)
        main_layout.addWidget(self.matter_display)

        # ASCII Table
        self.ascii_table_label = QLabel("Game State Overview:")
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

        dynamics_scroll = QScrollArea()
        dynamics_scroll.setWidgetResizable(True)
        dynamics_scroll.setWidget(self.dynamics_group)
        main_layout.addWidget(dynamics_scroll)

        # Set the layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def log_message(self, message):
        self.response_display.append(message)

    def initialize_game(self):
        context_file = self.context_selector.currentText()
        characters = load_characters(context_file)
        try:
            response = requests.post(INITIALIZE_URL, json=characters)
            response.raise_for_status()
            self.log_message("Game state initialized successfully!")
            self.refresh_game_state()
        except requests.exceptions.RequestException as e:
            self.log_message(f"Failed to initialize game state: {e}")

    def refresh_game_state(self):
        try:
            response = requests.get(ACTIVE_STATE_URL)
            response.raise_for_status()
            game_state = response.json()
            self.display_game_state(game_state)
        except requests.exceptions.RequestException as e:
            self.log_message(f"Error fetching game state: {e}")

    def display_game_state(self, game_state):
        # Display Matter of Fact
        matter_of_fact = game_state.get("matter_of_fact", [])
        self.matter_display.setPlainText("\n".join(f"- {fact}" for fact in matter_of_fact))

        # Display ASCII Table
        self.ascii_table.clear()
        self.ascii_table.append("Game State Overview:\n")
        self.ascii_table.append("=" * 40)

        # Display Players
        players = game_state.get("players", {})
        for player_id, player_data in players.items():
            self.ascii_table.append(f"Player ID: {player_id}, Name: {player_data['name']}")

        # Display Agents
        agents = game_state.get("agents", {})
        for agent_id, agent_data in agents.items():
            self.ascii_table.append(f"Agent ID: {agent_id}, Name: {agent_data['name']}")
        self.ascii_table.append("=" * 40)

        # Populate Agent Selector
        self.populate_agent_selector(agents)

        # Clear and display dynamics
        self.clear_dynamics()
        for agent_id, agent_data in agents.items():
            self.display_agent_dynamics(agent_data)

    def populate_agent_selector(self, agents):
        self.agent_selector.clear()
        for agent_id, agent_data in agents.items():
            self.agent_selector.addItem(agent_data["name"], agent_id)

    def display_agent_dynamics(self, agent_data):
        dynamics_label = QLabel(f"Dynamics for {agent_data['name']}:")
        self.dynamics_layout.addWidget(dynamics_label)

        latest_dynamics = agent_data["dynamics"][-1]  # Get the most recent dynamics
        for dynamic, value in latest_dynamics.items():
            label = QLabel(f"{dynamic.capitalize()}: {value * 100:.0f}%")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(value * 100))
            self.dynamics_layout.addWidget(label)
            self.dynamics_layout.addWidget(bar)

    def clear_dynamics(self):
        while self.dynamics_layout.count():
            widget = self.dynamics_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

    def talk_to_agent(self):
        selected_agent_name = self.agent_selector.currentText()
        selected_agent_id = self.agent_selector.currentData()
        user_input = self.message_input.toPlainText().strip()

        if not selected_agent_id or not user_input:
            self.log_message("Please select an agent and enter a message.")
            return

        # Log the payload being sent
        self.log_message(f"Talking to agent: {selected_agent_name} (ID: {selected_agent_id})")
        payload = {
            "agent_id": selected_agent_id,
            "player_id": "p1",
            "input": user_input
        }
        self.log_message(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(TALK_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            self.log_message(f"Agent: {data['response']}")
            self.refresh_game_state()
        except requests.exceptions.RequestException as e:
            self.log_message(f"Error talking to agent: {e}")


# Start the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
