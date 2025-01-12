import requests

# Define the WSL server URL
WSL_SERVER_URL = "http://192.168.1.100:5555"  # Replace with your WSL IP

# Example endpoint to talk to the agent
TALK_ENDPOINT = f"{WSL_SERVER_URL}/talk_to_agent"

# Example payload to send to the server
payload = {
    "agent_id": "agent1",
    "player_id": "player1",
    "input": "What is your mission?"
}

# Function to talk to the agent
def talk_to_agent():
    try:
        response = requests.post(TALK_ENDPOINT, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Agent's Response:", data["response"])
            print("Updated Dynamics:", data["agent_dynamics"])
        else:
            print("Failed to talk to agent. Error:", response.status_code, response.text)
    except Exception as e:
        print("Error communicating with the server:", str(e))

if __name__ == "__main__":
    talk_to_agent()
