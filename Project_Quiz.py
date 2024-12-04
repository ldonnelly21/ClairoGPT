import html
from quart import Quart, request, render_template_string
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
import time

import logging

# Set up logging to display errors
logging.basicConfig(level=logging.DEBUG)

# Initialize Quart app
app = Quart(__name__)
# HTML template for the page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <link href='https://fonts.googleapis.com/css?family=Tangerine' rel='stylesheet'>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Response</title>
    <style>
    html, body {
font-family: sans-serif;
font-size:1.4em;
margin: 0;
background: rgb(206, 205, 180);
}
form {
max-width: 800px;
margin: 0 auto;
padding: 16px;
border: 2px rgb(34, 44, 9);
color: rgb(34, 44, 9);
font-family: tangerine;
border: 2px dashed rgb(34, 44, 9);
padding: 32px;
}
h1, h2, h3 {
text-align: center;
color: rgb(34, 44, 9);
font-family: tangerine;
}
h1 {
font-size: 72px;
}
h2 {
font-size: 11px;
padding: 2px;
}
p {
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0 120px;
    font-family: tangerine;

    }
    input {
    background: rgb(255, 244, 242);
    width: 100%;
    }
    label {
    font-family: 'Tangerine', cursive;
    font-size: 36px; 
    display: block;
    margin-bottom: 16px;
}
   #send {
    background: rgb(135, 136, 90);
    font-family: 'Tangerine', cursive;
    font-size: 22px;
    cursor: pointer;
}
    </style>
</head>
<body>
    <h1>Get Charmed by Clairo GPT</h1>
    <form action="/chat" method="post">
        <label for="user_input">Ask me anything about Clairo!</label><br>
        <input type="text" id="user_input" name="user_input" required><br><br>
        <input type="submit" value="Get Charmed!" id="send">
    </form>
    {% if assistant_reply %}
    <h2>₊˚♡✧₊・♡・₊✧♡₊˚✧・₊✧₊˚♡・✧₊♡・₊✧</h2>
    <p>{{ assistant_reply }}</p>
    {% endif %}
</body>
</html>
'''

@app.route('/')
async def index():
    # Render the initial HTML page with no response yet
    return await render_template_string(html_template)

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        # Get user input from the form
        form_data = await request.form
        user_input = form_data['user_input']

        # Interact with OpenAI API
        assistant = client.beta.assistants.create(
            name="quiz master",
            description="You are a Charm by Clairo connoisseur.",
            model="gpt-4-turbo",
            tools=[{"type": "code_interpreter"}]
        )
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "When user inputs a question about Clairo, provide them with an answer relevant to what the user inputs."
                }
            ]
        )
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Output as HTML text."
        )
        while run.status != "completed":
            time.sleep(5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"\t\t{run}")

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            ).model_dump_json()

        # Extract the assistant's response
        json_data = json.loads(messages)
        values = []
        for item in json_data['data']:
            values.append(item['content'][0]['text']['value'])
            values = values.pop()
            assistant_response = values
            # Render the HTML page with the ChatGPT response
            return await render_template_string(html_template, assistant_reply=assistant_response)

    except Exception as e:
        # Log any errors
        app.logger.error(f"Error: {e}")
        return await render_template_string(html_template, assistant_reply="Something went wrong, please try again.")


if __name__ == '__main__':
    app.run(debug=True)
