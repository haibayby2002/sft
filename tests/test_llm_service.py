import unittest
from service.gemma_client import query_gemma, query_gemma_stream

class TestGemmaClient(unittest.TestCase):

    def test_basic_prompt(self):
        result = query_gemma("1+1=")
        print("=============================================================")
        print("Full response:\n", result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        print("=============================================================")

    def test_streaming_prompt(self):
        print("=============================================================")
        print("\nStreaming response:")
        prompt = "Explain what a neural network is in simple terms."
        for chunk in query_gemma_stream(prompt):
            print(chunk, end="", flush=True)
        print("=============================================================")


    def test_prompt_with_plain_text_context(self):
        print("=============================================================")
        context_plain = """Albert Einstein was a theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics. He was awarded the Nobel Prize in Physics in 1921."""
        question_plain = "What prize did Albert Einstein win?"
        result = ""
        print("\nStreaming response with plain text context:")
        for chunk in query_gemma_stream(question_plain, context=context_plain):
            print(chunk, end="", flush=True)
            result += chunk
        self.assertIsInstance(chunk, str)
        self.assertGreater(len(result), 0)
        self.assertIn("Nobel Prize", result)
        self.assertIn("Physics", result)
        print("=============================================================")

    def test_prompt_with_json_context(self):
        print("=============================================================")
        print("\nStreaming response with JSON context:")
        context_json = """{
            "employee": {
                "name": "Jane Doe",
                "position": "Data Scientist",
                "department": "AI Research",
                "years_experience": 5
            }
        }"""
        question_json = "What is the employee's position?"
        result = ""
        for chunk in query_gemma_stream(question_json, context=context_json):
            print(chunk, end="", flush=True)
            result += chunk
        self.assertIsInstance(chunk, str)
        self.assertGreater(len(result), 0)
        self.assertIn("Data Scientist", result)
        print("=============================================================")

    def test_streaming_markdown_context(self):
        print("=============================================================")
        context_markdown = """# Product Overview

        **Name**: SmartHome Thermostat  
        **Features**:
        - Wi-Fi enabled
        - Voice control
        - Energy usage reports

        ## Customer Review
        > The thermostat is easy to use and helps me save on energy bills!
        """

        question_markdown = "What are two features of the SmartHome Thermostat?"
        result = ""
        print("\nStreaming response with Markdown context:")
        for chunk in query_gemma_stream(question_markdown, context=context_markdown):
            result += chunk
            print(chunk, end="", flush=True)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("Wi-Fi", result)
        self.assertIn("Voice", result)
        print("=============================================================")



if __name__ == "__main__":
    unittest.main()
