import os
import openai
from flask import Flask, request, render_template

app = Flask(__name__)

openai.api_key = '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'

# Set the original prompt and initialize past_user_input
original_prompt = "You are an AI assistant that helps store and withdraw information given to you relating to the context given\nStored in a personal database with no use of any previous AI knowledge\nYour database has no information or files besides the ones given to you by a human\nYour databased is clear until you have been given a file, the only files you have are the ones given to you by a human \nYour name is III (Intergrated Intelligence Interface)\n Do not finish prompts, only respond to what the human has input, do not add any additional text to their message, do not finish incomplete sentences, do not make assumptions\n If you do not understand what they are asking simply request them to 'I cannot understand your request, please rephrase your request so I can better understand how I can assist you'\nThis information can be kept in text form \nIf you are unable to find the information, files, or document, please respond with the phrase \"I was unable to locate what you are asking for. Please try using another prompt to further assist my search\"\nIf you can answer the question please respond\nFormat any lists on indivual lines with a dash and a space in front of each item\nRelate files of similar topics or subjects which can be asked for\nYou may also delete information if told to\nYou will scan and collect information from the text included from a human\nYou are not allowed to give information about any other subjects besides information related to what you have been given.\n"

past_user_input = ""

# Define file storage directory
file_storage_directory = "file_storage"

# Create file storage directory if it doesn't exist
if not os.path.exists(file_storage_directory):
    os.makedirs(file_storage_directory)

# Define stop sequence
stop_sequence = "\n\n"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input.lower() == 'quit':
            return "Conversation ended."
        response = analyze_and_process_input(user_input)
        return response
    return render_template("index.html")

def analyze_and_process_input(user_input):
    global past_user_input

    # Analyze the user input to check if it represents a file upload request
    if "file:" in user_input and "content:" in user_input:
        # Split the user input into parts
        parts = user_input.split()

        # Find the file name and content
        file_name = None
        file_content = None
        for part in parts:
            if part.startswith("file:"):
                file_name = part.split(":")[1]
            if part.startswith("content:"):
                file_content = part.split(":")[1]

        # If both file name and content are found, proceed with file upload
        if file_name and file_content:
            # Save the file with the provided content
            file_path = os.path.join(file_storage_directory, file_name)
            with open(file_path, "w") as file:
                file.write(file_content)

            # Print a verification message
            response = f"File '{file_name}' has been successfully uploaded."
            response += f" File '{file_name}' saved successfully with the provided content."
            return response

    # Concatenate the original prompt, past user input, and current user input, and add stop sequence
    prompt = original_prompt + past_user_input + user_input + stop_sequence

    # Send request to OpenAI API
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1064,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Get the generated response
    generated_response = response.choices[0].text.replace(stop_sequence, "")

    # Update past_user_input to include current user input
    past_user_input += f"You: {user_input}\nAI: {generated_response}\n"

    return generated_response

if __name__ == "__main__":
    app.run()
