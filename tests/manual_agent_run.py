"""
Conversation turn-based Testbench of the agent's performance.
Select an example input file and write your query. Then run the agent to get the response.
"""

import json
from lf_toolkit.chat import ChatRequest
from src.module import chat_module

# File path for the input text
path = "src/agent/utils/example_inputs/"
input_file = path + "example_input_3.json"

# Step 1: Read the input file
with open(input_file, "r") as file:
    raw_text = file.read()

try:
    parsed_json = json.loads(raw_text)

    # NOTE: #### This is the testing message #####
    message = "What are my submission attempts and feedback for the current part?"
    # NOTE: ########################################

    # Replace the last user message with the testing message
    parsed_json["messages"][-1]["content"] = message

    # Step 2: Build and validate the ChatRequest
    request = ChatRequest.model_validate(parsed_json)

    # Step 3: Call the chat module
    response = chat_module(request)

    print(response.model_dump_json(indent=4))

except json.JSONDecodeError as e:
    print("Error decoding JSON:", e)
