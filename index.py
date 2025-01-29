import json
try:
    from .src.module import chat_module
    from .src.agents.utils.types import JsonType
except ImportError:
    from src.module import chat_module
    from src.agents.utils.types import JsonType

def handler(event: JsonType, context):
    """
    Lambda handler function
    Args:
        event (JsonType): The AWS Lambda event received by the gateway.
        context (Any): The AWS Lambda context object.

    """
    # Log the input event for debugging purposes
    print("Received event:", json.dumps(event, indent=2))

    if "body" not in event:
        return {
            "statusCode": 400,
            "body": "Missing 'body' key in event. Please confirm the key in the json body."
        }
    body = json.loads(event["body"])
        
    if "message" not in body:
        return {
            "statusCode": 400,
            "body": "Missing 'message' key in event. Please confirm the key in the json body."
        }
    if "params" not in body:
        return {
            "statusCode": 400,
            "body": "Missing 'params' key in event. Please confirm the key in the json body. Make sure it contains the necessary conversation_id."
        }
    
    message = body["message"]
    params = body["params"]

    print("Message:", message, "Params:", params)

    try:
        chatbot_response = chat_module(message, params)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"An error occurred within the chat_module(): {str(e)}"
        }

    # Create a response
    response = {
        "statusCode": 200,
        "body": chatbot_response
    }

    print("Response:", json.dumps(response, indent=2))

    return response