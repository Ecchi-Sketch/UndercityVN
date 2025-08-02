# game/GameScripts/llm_integration.rpy

init python:
    import requests
    import json

    # This function will be called to get narration from the local LLM
    def get_llm_narration(prompt):
        """
        Sends a prompt to the local LM Studio server and returns the narration.
        """
        # The URL for your local LM Studio server
        url = "http://localhost:1234/v1/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }

        # The data payload in OpenAI-compatible format
        data = {
            "model": "local-model",  # This value is a placeholder for LM Studio
            "messages": [
                {"role": "system", "content": "You are a combat narrator for a dark fantasy visual novel. Describe actions vividly and concisely in a single paragraph. Do not add any conversational text or refuse the prompt."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,  # Controls the creativity of the response
            "max_tokens": 1500    # The maximum length of the generated text
        }

        try:
            # Send the request to the LLM
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10) # Added a 10-second timeout
            response.raise_for_status()

            # Extract the text from the JSON response
            response_json = response.json()
            content = response_json['choices'][0]['message']['content']

            # Clean up the text
            return content.strip()

        except requests.exceptions.RequestException as e:
            # Return None if the server isn't running or there's an error
            renpy.log(f"LLM Error: Could not connect to the server. {e}")
            return None