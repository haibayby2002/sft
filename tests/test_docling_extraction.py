from docling.document_converter import DocumentConverter

def convert_pdf_to_markdown(pdf_path):
    """
    Converts a PDF document to Markdown using IBM Docling.

    Args:
        pdf_path (str): The path to the input PDF file or a URL.
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)

        # Docling typically returns a 'Document' object with structured content
        # You can then export this content to Markdown or JSON
        markdown_output = result.document.export_to_markdown()

        # You can print or save this Markdown content
        print(f"Markdown content from '{pdf_path}':\n")
        print(markdown_output[:1000]) # Print first 1000 characters for brevity

        # Optionally, save to a file
        output_filename = f"{pdf_path.split('/')[-1].split('.')[0]}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        print(f"\nFull Markdown content saved to: {output_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Replace 'your_document.pdf' with the actual path to your PDF file
    # pdf_file = "C:\\Users\\dell\\Downloads\\CV___Harvard_like.pdf"
    pdf_file = "C:\\Users\\dell\\Downloads\\Block as a Supply Chain Service.pdf"
    convert_pdf_to_markdown(pdf_file)