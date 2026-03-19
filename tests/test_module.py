import unittest
from lf_toolkit.chat import ChatRequest, ChatResponse
from src.module import chat_module


def make_request(**kwargs):
    defaults = {
        "messages": [{"role": "USER", "content": "Hello, World"}],
        "conversationId": "1234Test",
    }
    defaults.update(kwargs)
    return ChatRequest.model_validate(defaults)


class TestChatModuleFunction(unittest.TestCase):
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
    """

    def test_missing_conversation_id(self):
        # conversationId is required by chat_module even though it's optional in ChatRequest
        request = make_request(conversationId=None)

        with self.assertRaises(Exception) as cm:
            chat_module(request)

        self.assertIn("Internal Error", str(cm.exception))
        self.assertIn("conversation id", str(cm.exception))

    def test_agent_output(self):
        # Checking the output of the agent
        request = make_request()

        result = chat_module(request)

        self.assertIsInstance(result, ChatResponse)
        self.assertIsNotNone(result.output)
        self.assertIsNotNone(result.output.content)

    def test_processing_time_in_metadata(self):
        # Checking the processing time is included in the response metadata
        request = make_request()

        result = chat_module(request)

        self.assertIsNotNone(result.metadata)
        self.assertIn("processingTimeMs", result.metadata)
        self.assertGreaterEqual(result.metadata["processingTimeMs"], 0)
