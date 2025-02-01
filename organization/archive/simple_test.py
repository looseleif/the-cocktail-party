from llama_cpp import Llama

# Load the model
try:
    print("Loading the model...")
    llm = Llama("./llama-3.2-3b-instruct.Q8_0.gguf", n_ctx=1024, verbose=True)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Test the model with a higher max_tokens value
try:
    print("Running a test prompt...")
    response = llm("hello what is your name?", max_tokens=150)
    print("Model response:")
    print(response['choices'][0]['text'].strip() if 'choices' in response else "No response received")
except Exception as e:
    print(f"Error during inference: {e}")

