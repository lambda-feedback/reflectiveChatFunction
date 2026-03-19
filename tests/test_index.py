import unittest
import json
from index import handler


def make_event(body: dict) -> dict:
    return {"body": json.dumps(body)}


BASE_BODY = {
    "messages": [{"role": "USER", "content": "Hello, World"}],
    "conversationId": "1234Test",
}


class TestChatIndexFunction(unittest.TestCase):
    """
    TestCase Class used to test the algorithm.
    ---
    Tests are used here to check that the algorithm written
    is working as it should.

    It's best practise to write these tests first to get a
    kind of 'specification' for how your algorithm should
    work, and you should run these tests before committing
    your code to AWS.

    Read the docs on how to use unittest here:
    https://docs.python.org/3/library/unittest.html

    Use module() to check your algorithm works
    as it should.

    The expected input of the handler is a JsonType matching ChatRequest.
    """

    def test_missing_messages(self):
        # messages is required — omitting it should return 400
        body = {k: v for k, v in BASE_BODY.items() if k != "messages"}
        result = handler(make_event(body), None)
        self.assertEqual(result.get("statusCode"), 400)

    def test_invalid_json_body(self):
        result = handler({"body": "not valid json"}, None)
        self.assertEqual(result.get("statusCode"), 400)

    def test_correct_arguments(self):
        result = handler(make_event(BASE_BODY), None)
        self.assertEqual(result.get("statusCode"), 200)

    def test_correct_response(self):
        result = handler(make_event(BASE_BODY), None)
        self.assertEqual(result.get("statusCode"), 200)
        body = json.loads(result["body"])
        self.assertIn("output", body)
        self.assertIn("content", body["output"])
