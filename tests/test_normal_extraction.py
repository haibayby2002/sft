import unittest
import os

from service.docling_service import extract_text_by_page

class TestDoclingExtraction(unittest.TestCase):
    def setUp(self):
        # Set this path to a valid PDF file for testing
        # self.sample_pdf_path = "C:\\Users\\dell\\Downloads\\Module 1 Transcript - Blockchains, Tokens, and The Decentralized Future.pdf"
        # self.sample_pdf_path = "C:\\Users\\dell\\Downloads\\CV___Harvard_like.pdf"
        self.sample_pdf_path = "C:\\Users\\dell\\Downloads\\Block as a Supply Chain Service.pdf"
    def test_file_exists(self):
        """Check that the test PDF file exists."""
        self.assertTrue(os.path.exists(self.sample_pdf_path), "Sample PDF file not found.")

    def test_extract_text_by_page(self):
        """Test that text is extracted per page and format is correct."""
        results = extract_text_by_page(self.sample_pdf_path)
        print(results)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "No pages extracted")

        for page in results:
            self.assertIn("page_number", page)
            self.assertIn("text", page)
            self.assertIsInstance(page["page_number"], int)
            self.assertIsInstance(page["text"], str)

    def test_nonexistent_file(self):
        """Test that an error is raised if the file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            extract_text_by_page("nonexistent.pdf")

if __name__ == "__main__":
    unittest.main()
