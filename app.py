import os
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import openai

# Load the .env file
load_dotenv()

# Check for file existence
try:
    # Check for .env file existence
    if not os.path.exists(".env"):
        raise ValueError(".env file not found")

    # Load environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
    print("Open AI Key:", openai_key)
    print("Slack Bot Token:", slack_bot_token)

    # Check the validity of environment variables
    if not openai_key or not slack_bot_token:
        raise ValueError("One or more required environment variables are missing or empty")

    # Use variables
    openai.api_key = openai_key
    app = App(token=slack_bot_token)

    # Additional checks or usage

except ValueError as e:
    print(f"Error: {e}")


# Load the system message from the JSON file
with open('system_message.json', 'r') as file:
    system_message = json.load(file)

# Function to fetch response from OpenAI using Chat Completions
def ask_openai(question):
    try:
        # Include the loaded system message in the chat completion request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                system_message,
                {"role": "user", "content": question}
            ]
        )
        # Extracting and returning the chat completion response
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return "I'm having trouble thinking right now. Please try again later."

# Handling app_mention events in Slack
@app.event("app_mention")
def handle_app_mention_events(body, say):
    event = body['event']
    user_question = event['text'].split('>')[1].strip()  # Extracting the question text
    ai_response = ask_openai(user_question)  # Generating response using OpenAI
    say(ai_response)  # Responding in Slack

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
