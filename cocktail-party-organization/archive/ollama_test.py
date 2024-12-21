import requests
import threading
import json

# Function to query a model
def query_model(model_name, system_context, user_input, results):
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_input}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results[model_name] = response.json()
            print(f"Response from {model_name}: {results[model_name]}")
        else:
            print(f"Failed to query {model_name}: {response.status_code} {response.text}")
            results[model_name] = {"error": response.text}
    except Exception as e:
        print(f"Error querying {model_name}: {str(e)}")
        results[model_name] = {"error": str(e)}

# Function to send responses to both servers
def send_to_servers(response, linux_server_url, unity_server_url):
    headers = {"Content-Type": "application/json"}

    # Send to Linux WSL server
    try:
        linux_response = requests.post(linux_server_url, headers=headers, json=response)
        if linux_response.status_code == 200:
            print("Response sent to Linux server successfully!")
        else:
            print(f"Failed to send to Linux server: {linux_response.status_code} {linux_response.text}")
    except Exception as e:
        print(f"Error sending to Linux server: {str(e)}")

    # Send to Unity server
    try:
        unity_response = requests.post(unity_server_url, headers=headers, json=response)
        if unity_response.status_code == 200:
            print("Response sent to Unity server successfully!")
        else:
            print(f"Failed to send to Unity server: {unity_response.status_code} {unity_response.text}")
    except Exception as e:
        print(f"Error sending to Unity server: {str(e)}")

# Function to run multiple models at once
def run_models(models, system_context, user_input, linux_server_url, unity_server_url):
    threads = []
    results = {}
    
    for model_name in models:
        thread = threading.Thread(target=query_model, args=(model_name, system_context, user_input, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Send responses to both servers
    send_to_servers(results, linux_server_url, unity_server_url)

# Define the models, system context, and user input
models = ["tinyllama", "llama3.2"]
system_context = "You are a persuasive assistant trying to convince someone to let you use their phone."
user_input = "Why should I let you use my phone?"

# Define server URLs
linux_server_url = "http://<linux_server_ip>:<linux_server_port>/endpoint"  # Replace with actual URL
unity_server_url = "http://<unity_server_ip>:<unity_server_port>/endpoint"  # Replace with actual URL

# Run the models and send responses
run_models(models, system_context, user_input, linux_server_url, unity_server_url)
