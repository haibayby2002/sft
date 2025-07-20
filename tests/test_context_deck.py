import unittest
from data.models.deck import load_context_from_deck

class TestDeckContext(unittest.TestCase):
    def setUp(self):
        # Set a valid deck ID for testing
        pass

    def test_load_context_from_deck_1(self):
        """Test loading context from a deck."""
        test_deck_id = 1
        context = load_context_from_deck(test_deck_id)
        print(context)
        self.assertIsInstance(context, list)
        self.assertGreater(len(context), 0, "No slides found in the deck")

        for slide in context:
            self.assertIn("slide_id", slide)
            self.assertIn("title", slide)
            self.assertIn("pages", slide)
            self.assertIsInstance(slide["pages"], list)

    def test_load_context_from_deck_2(self):
        """Test loading context from a deck."""
        test_deck_id = 2
        context = load_context_from_deck(test_deck_id)
        print(context)
        self.assertIsInstance(context, list)
        self.assertGreater(len(context), 0, "No slides found in the deck")

        for slide in context:
            self.assertIn("slide_id", slide)
            self.assertIn("title", slide)
            self.assertIn("pages", slide)
            self.assertIsInstance(slide["pages"], list)

    def test_load_context_from_deck_3(self):
        """Test loading context from a deck."""
        test_deck_id = 3
        context = load_context_from_deck(test_deck_id)
        print(context)
        self.assertIsInstance(context, list)
        self.assertGreater(len(context), 0, "No slides found in the deck")

        for slide in context:
            self.assertIn("slide_id", slide)
            self.assertIn("title", slide)
            self.assertIn("pages", slide)
            self.assertIsInstance(slide["pages"], list)

    def test_load_context_from_deck_4(self):
        """Test loading context from a deck."""
        test_deck_id = 4
        context = load_context_from_deck(test_deck_id)
        print(context)
        self.assertIsInstance(context, list)
        self.assertGreater(len(context), 0, "No slides found in the deck")

        for slide in context:
            self.assertIn("slide_id", slide)
            self.assertIn("title", slide)
            self.assertIn("pages", slide)
            self.assertIsInstance(slide["pages"], list)

if __name__ == "__main__":
    unittest.main()