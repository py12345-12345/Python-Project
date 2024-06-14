import os
import fitz
import datetime
import re
import nltk

# Download nltk resources (run this line once)
nltk.download('punkt')

def read_objectionable_words(file_path):
    """
    Read objectionable words from a text file.

    Parameters:
    file_path (str): The path to the text file containing objectionable words.

    Returns:
    list: A list of objectionable words.
    """
    with open(file_path, "r") as file:
        objectionable_words = [word.strip() for word in file.readlines()]
    return objectionable_words

def detect_and_highlight(pdf_file, objectionable_words, base_output_dir):
    """
    Detect objectionable words in a PDF and highlight them.

    Parameters:
    pdf_file (str): The path to the PDF file.
    objectionable_words (list): A list of objectionable words to detect and highlight.
    base_output_dir (str): The base output directory where the results will be saved.
    """
    try:
        # Create output directory based on current date
        output_dir = os.path.join(base_output_dir, datetime.datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(output_dir, exist_ok=True)

        # Open the PDF file
        pdf_document = fitz.open(pdf_file)

        # Initialize list to store findings
        findings = []

        # Iterate over each page in the PDF
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            text = page.get_text()

            # Initialize list to store objectionable words found on the page
            objectionable_words_found = []

            # Tokenize text into words
            words = nltk.word_tokenize(text)

            # Highlight objectionable words
            for word in objectionable_words:
                for w in words:
                    if w.lower() == word.lower():
                        matches = re.finditer(r'\b{}\b'.format(re.escape(w)), text, re.IGNORECASE)
                        for match in matches:
                            try:
                                rect = match.span()  # Get the coordinates of the matched word
                                annot = page.add_rect_annot(rect)  # Add a rectangle annotation
                                annot.set_colors(stroke=(1, 0, 0), fill=(1, 1, 0), alpha=0.4)  # Set annotation colors

                                objectionable_words_found.append(word)
                            except Exception as e:
                                print(f"Error adding annotation on page {page_number + 1} for word '{word}': {e}")

            # Add page findings to the list
            if objectionable_words_found:
                findings.append((page_number + 1, objectionable_words_found))

        # Save the output PDF with highlighted words
        output_pdf_path = os.path.join(output_dir, f"highlighted_{os.path.basename(pdf_file)}")
        pdf_document.save(output_pdf_path)

        # Write findings to text file
        output_text_path = os.path.join(output_dir, f"{os.path.basename(pdf_file)}_objectionable_words.txt")
        with open(output_text_path, "w") as text_file:
            for idx, (page_num, words_found) in enumerate(findings, start=1):
                text_file.write(f"{idx}. - Page {page_num}, Word(s): {', '.join(words_found)}\n")
            text_file.write(f"Total words detected are {sum(len(words) for _, words in findings)}")

        print(f"Highlighted PDF saved as {output_pdf_path}")
        print(f"Findings saved in {output_text_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Base output directory
    base_output_dir = "F:/AQC/Tests"

    # Specify the path to the objectionable words file
    objectionable_words_file = "objectionable_words.txt"

    # Read objectionable words from the file
    objectionable_words = read_objectionable_words(objectionable_words_file)

    # Specify the path to the PDF file to be processed
    pdf_file = "F:/prohibited words/1143936.pdf"  # Add the path to your PDF file here

    # Process the PDF file
    detect_and_highlight(pdf_file, objectionable_words, base_output_dir)

if __name__ == "__main__":
    main()