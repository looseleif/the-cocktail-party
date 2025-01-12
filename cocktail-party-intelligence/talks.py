from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QTextEdit, 
    QWidget, QComboBox, QGroupBox, QScrollArea, QProgressBar, QTabWidget, QGridLayout
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

        # Main layout with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_overview_tab(), "Overview")
        self.tab_widget.addTab(self.create_dynamics_tab(), "Dynamics")
        self.tab_widget.addTab(self.create_interaction_tab(), "Interaction")

        # Set central widget
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.context_label = QLabel("Select Context:")
        layout.addWidget(self.context_label)

        self.context_selector = QComboBox()
        self.context_selector.addItems(get_json_files())
        layout.addWidget(self.context_selector)

        self.init_button = QPushButton("Initialize Game State")
        self.init_button.clicked.connect(self.initialize_game)
        layout.addWidget(self.init_button)

        self.matter_label = QLabel("Matter of Fact:")
        layout.addWidget(self.matter_label)

        self.matter_display = QTextEdit()
        self.matter_display.setReadOnly(True)
        layout.addWidget(self.matter_display)

        self.ascii_table_label = QLabel("Game State Overview:")
        layout.addWidget(self.ascii_table_label)

        self.ascii_table = QTextEdit()
        self.ascii_table.setReadOnly(True)
        layout.addWidget(self.ascii_table)

        widget.setLayout(layout)
        return widget

    def create_dynamics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.dynamics_group = QGroupBox("Agent Dynamics")
        self.dynamics_layout = QVBoxLayout()
        self.dynamics_group.setLayout(self.dynamics_layout)

        dynamics_scroll = QScrollArea()
        dynamics_scroll.setWidgetResizable(True)
        dynamics_scroll.setWidget(self.dynamics_group)
        layout.addWidget(dynamics_scroll)

        widget.setLayout(layout)
        return widget

    def create_interaction_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.agent_selector_label = QLabel("Select Agent:")
        layout.addWidget(self.agent_selector_label)

        self.agent_selector = QComboBox()
        layout.addWidget(self.agent_selector)

        self.input_label = QLabel("Enter your message:")
        layout.addWidget(self.input_label)

        self.message_input = QTextEdit()
        layout.addWidget(self.message_input)

        self.send_button = QPushButton("Talk to Agent")
        self.send_button.clicked.connect(self.talk_to_agent)
        layout.addWidget(self.send_button)

        self.response_label = QLabel("Agent Response:")
        layout.addWidget(self.response_label)

        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        layout.addWidget(self.response_display)

        widget.setLayout(layout)
        return widget

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
        group_box = QGroupBox(agent_data['name'])
        layout = QGridLayout()

        # Access the most recent dynamics
        latest_dynamics = agent_data.get("dynamics", [{}])[-1]
        emotion_changes = agent_data.get("emotion_changes", {})

        for i, (dynamic, value) in enumerate(latest_dynamics.items()):
            if not isinstance(value, int):
                continue  # Ensure only integer values are processed

            label = QLabel(f"{dynamic.capitalize()}:")
            bar = QProgressBar()
            bar.setRange(0, 10)
            bar.setValue(value)

            # Determine if there's a change to display
            change = emotion_changes.get(dynamic, None)
            if change is not None:
                change_indicator = QLabel("▲" if change > 0 else "▼")
                change_indicator.setStyleSheet("color: green;" if change > 0 else "color: red;")
            else:
                change_indicator = QLabel(" ")  # No change indicator for initial load

            layout.addWidget(label, i, 0)
            layout.addWidget(bar, i, 1)
            layout.addWidget(change_indicator, i, 2)

        group_box.setLayout(layout)
        self.dynamics_layout.addWidget(group_box)

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

        payload = {
            "agent_id": selected_agent_id,
            "player_id": "p1",
            "input": user_input
        }

        try:
            response = requests.post(TALK_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            self.log_message(f"Agent: {data['response']}")

            # Update game state after interaction
            self.refresh_game_state()
        except requests.exceptions.RequestException as e:
            self.log_message(f"Error talking to agent: {e}")

# Start the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
