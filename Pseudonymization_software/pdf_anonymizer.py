import fitz
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PIL import Image
import os
import re
import io
import pandas as pd

from memory import RunTimeMemory


class PDFAnonymizer:
    def __init__(self, memory, save_path=None, pdf_paths=None, replacements=None):
        self.memory = memory
        self.pdf_paths = pdf_paths
        self.replacements = self.memory.found_entities
        self.save_path = save_path
        self.skipped_images = []

    def set_save_path(self, path):
        self.save_path = path

    def validate_paths(self):
        if not os.path.isdir(self.save_path):
            print(ValueError(f"The save path {self.save_path} does not exist or is not a directory."))
            return
        for path in self.pdf_paths:
            if not os.path.isfile(path):
                print(ValueError(f"The file path {path} does not exist or is not a file."))
                return

    @staticmethod
    def replace_extension_to_pdf(file_path):
        # Split the file path into root and extension
        root, ext = os.path.splitext(file_path)
        # Check if the extension is already '.pdf', if not replace it with '.pdf'
        if ext.lower() != '.pdf':
            return root + '.pdf'
        return file_path

    def replace_words(self):
        if not self.save_path:
            raise Exception("Save path not set for pseudonym_pdfs")
        pdf_paths = list(self.memory.file_data.keys())
        num = len(pdf_paths)
        for ind, pdf_path in enumerate(pdf_paths, start=1):
            if pdf_path in self.memory.needs_ocr:
                continue
            data = self.memory.file_data[pdf_path]
            #data = self.extract_pdf_text_with_meta_fitz(pdf_path)
            data = self.improved_anonymize_text(data)
            pdf_path = self.replace_extension_to_pdf(pdf_path)
            self.recreate_pdf_with_pages(data, pdf_path)
            print(f"Processed {ind} files from total of {num} files.")
        print(f"Processed all {num} files.")

    def extract_pdf_text_with_meta_fitz(self, pdf_path):
        data = []

        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                # Determine page orientation
                page_orientation = 'landscape' if page.rect.width > page.rect.height else 'portrait'
                page_data = {'page': page_num, 'content': [], 'orientation': page_orientation,
                             'size': (page.rect.width, page.rect.height)}

                # Extract text with meta-information
                text_instances = page.get_text("dict")["blocks"]
                for inst in text_instances:
                    if inst["type"] == 0:  # Text
                        for line in inst["lines"]:
                            for span in line["spans"]:
                                text_data = {
                                    'type': 'text',
                                    'text': span['text'],
                                    'font': span['font'],
                                    'size': span['size'],
                                    'location': (span['bbox'][0], span['bbox'][1], span['bbox'][2], span['bbox'][3])
                                }
                                page_data['content'].append(text_data)

                # Extract images
                """image_instances = page.get_images(full=True)
                image_list = doc.get_page_images(page_num, full=True)


                try:
                    for item, img_inst in zip(image_list, image_instances):
                        xref = img_inst[0]
                        img_extract_data = doc.extract_image(xref)
                        try:
                            bbox = page.get_image_bbox(item)
                            image_data = {
                                'type': 'image',
                                'image': img_extract_data.get('image'),
                                'extension': img_extract_data['ext'],
                                'location': (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
                            }
                            page_data['content'].append(image_data)
                        except ValueError as e:
                            self.skipped_images.append({"file": pdf_path, "page": page_num, "error":e, "data":xref})
                            #print(f"Skipping image with xref {xref} due to error: {e}")
                except Exception as er:
                    print(f"This error occurred: {er}")"""
                data.append(page_data)
        pd.DataFrame(self.skipped_images).to_csv("Skipped_images.csv", encoding='utf-8', index=False)
        return data

    def extract_pdf_text_with_meta(self, pdf_path):
        data = []
        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    text_data = {
                                        'text': character.get_text(),
                                        'font': character.fontname,
                                        'size': character.size,
                                        'location': character.bbox}
                                    data.append(text_data)
        return data

    def improved_anonymize_text(self, data):
        # Build a single regex pattern that matches any of the words to replace.
        # Sort the words by length in descending order to ensure longer matches are found first.
        pattern = '|'.join(
            re.escape(word['word']) for word in sorted(self.replacements, key=lambda x: len(x['word']), reverse=True))
        regex = re.compile(pattern)

        def replace_func(match):
            word = match.group(0)
            # Find the replacement for the matched word. Assumes self.replacements is a list of dicts with 'word' and 'replacement' keys.
            for replacement in self.replacements:
                if replacement['word'] == word:
                    return replacement['replacement']
            return word  # Return the word itself if no replacement is found (should not happen with a well-defined replacements list).

        for page_data in data:
            for content_item in page_data['content']:
                if content_item['type'] == 'text':
                    # Use the regex with replace_func to replace all matches in a single pass.
                    content_item['text'] = regex.sub(replace_func, content_item['text'])

        return data



    def recreate_pdf_with_pages(self, data, pdf_path):
        new_file_name = "auto_anom_" + pdf_path[126:]  # Extracts a substring of pdf_path starting at index 33
        #new_file_name = "auto_anom_" + os.path.basename(pdf_path)
        output_pdf_path = os.path.join(self.save_path, new_file_name.replace("\\", "__"))
        c = canvas.Canvas(output_pdf_path)

        for page in data:
            try:
                width, height = page['size']
                c.setPageSize((width, height))
            except Exception as e:
                print(Warning(f"Set page size failed due to this error: {e}\nUsing A4 size now."))
                page_orientation = 'portrait'  # Default orientation
                width, height = A4  # Default to A4 portrait
                if page.get('orientation', 'portrait') == 'landscape':
                    page_orientation = 'landscape'
                    width, height = landscape(A4)
                c.setPageSize((width, height))

            for item in page['content']:
                if item['type'] == 'text':
                    # Handle text
                    text = item['text']
                    font = item['font']
                    size = item['size']
                    x0, y0, x1, y1 = item['location']
                    y = height - y1  # Adjust for ReportLab's coordinate system

                    c.setFont("Helvetica", size)
                    c.drawString(x0, y, text)

                elif item['type'] == 'image':
                    try:
                        # Handle images
                        image_data = item['image']
                        x0, y0, x1, y1 = item['location']
                        x, y, w, h = x0, height - y1, x1 - x0, y1 - y0  # Adjust dimensions and position

                        # Use PIL to open the image from binary data
                        # image = Image.open(io.BytesIO(image_data).getvalue())
                        print((w, h))
                        image = Image.frombytes('RGB', (round(w), round(h)), io.BytesIO(image_data).getvalue())
                        print(image)
                        c.drawInlineImage(image, x, y, width=w, height=h)
                    except Exception as err:
                        print(f"GOT THIS ERROR: {err}")
            c.showPage()  # End the current page and start a new one
        c.save()

