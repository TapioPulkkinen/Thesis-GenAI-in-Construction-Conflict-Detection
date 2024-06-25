import fitz
import os
from docx2pdf import convert as convert_to_pdf
from doc2docx import convert as convert_to_docx


class DirReader:

    @staticmethod
    def get_all_files_from_dir(path, max_depth, current_depth=0):
        if not os.path.isdir(path):
            raise NotADirectoryError("DirReader: Path is not a directory!")
        file_paths = []
        if path.startswith('"') or path.endswith('"'):
            path = path.strip('"')
        try:
            if current_depth > max_depth:
                return []
            # Iterate through items in the directory
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                # If the item is a directory, recursively call this function
                if os.path.isdir(item_path):
                    file_paths += DirReader.get_all_files_from_dir(item_path, max_depth, current_depth + 1)
                # If the item is a file, add its path to the list
                elif os.path.isfile(item_path):
                    file_paths.append(item_path)
        except Exception as e:
            raise Exception(f"DirReader: Error occurred while reading directory: {e}")
        return file_paths


class FileReader:

    def __init__(self, memory, chunking: bool = False, chunk_max_length: int = 5000, chunk_endings: list = None, use_ocr_if_needed: bool = True):
        self.memory = memory
        if chunk_endings is None:
            chunk_endings = ['\n\n', '\n']
        self.chunking = chunking
        self.chunk_max_length = chunk_max_length
        self.chunk_endings = chunk_endings
        self.pdf_file_paths = []
        self.use_ocr_if_needed = use_ocr_if_needed

    def set_chunking_enabled(self, is_enabled):
        if is_enabled:
            self.chunking = True
        else:
            self.chunking = False

    def get_allowed_file_types(self):
        return list(self.file_readers().keys())

    def process_file(self, file_path):
        name, file_extension = os.path.splitext(file_path)
        read_function = self.file_readers().get(file_extension)
        if read_function is None:
            raise TypeError(f"FileReader: Unsupported file type '{file_extension}' for file {file_path}. File wasn't read.")
        try:
            data = read_function(file_path)
            text = ''.join(item['text'] for page in data for item in page['content'] if item['type'] == 'text')
            """for page in data:
                for item in page['content']:
                    if item['type'] == 'text':
                        text += item['text']"""
            if len(text) < 10:
                self.memory.needs_ocr.append(file_path)
                return False
            else:
                self.memory.file_data[file_path] = data
                return True
        except Exception as err:
            raise Exception(f"FileReader: While reading file, this error occurred: {err}")

    def file_readers(self):
        return {
            #'.txt': self.read_txt_file,
            #'.TXT': self.read_txt_file,
            '.pdf': self.read_pdf_file_with_meta,
            '.PDF': self.read_pdf_file_with_meta,
            '.docx': self.read_docx_file,
            '.doc': self.read_doc_file,
            '.DOC': self.read_doc_file,
        }

    def read_txt_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def read_pdf_file_with_meta(self, file_path):  # TODO: enable OCR
        data = []
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc):
                # Determine page orientation
                page_orientation = 'landscape' if page.rect.width > page.rect.height else 'portrait'
                page_data = {'page': page_num, 'content': [], 'orientation': page_orientation, 'size': (page.rect.width, page.rect.height)}
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
                                    'size': round(span['size'], 1),
                                    'location': (round(span['bbox'][0], 1), round(span['bbox'][1], 1), round(span['bbox'][2], 1), round(span['bbox'][3], 1))}
                                page_data['content'].append(text_data)
                data.append(page_data)
        return data

    def convert_doc_to_docx(self, doc_path, docx_path):
        convert_to_docx(doc_path, docx_path)

    def convert_docx_to_pdf(self, docx_path, pdf_path):
        convert_to_pdf(docx_path, pdf_path)

    def read_doc_file(self, file_path):
        temp_folder = "temp_files"
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        temp_path = os.path.join(temp_folder, base_filename + ".docx")
        pdf_path = os.path.join(temp_folder, base_filename + ".pdf")

        self.convert_doc_to_docx(file_path, temp_path)
        self.convert_docx_to_pdf(temp_path, pdf_path)
        data = self.read_pdf_file_with_meta(pdf_path)
        os.remove(temp_path)
        os.remove(pdf_path)
        return data

    def read_docx_file(self, file_path):
        temp_folder = "temp_files"
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        pdf_path = os.path.join(temp_folder, base_filename + ".pdf")

        self.convert_docx_to_pdf(file_path, pdf_path)
        data = self.read_pdf_file_with_meta(pdf_path)
        os.remove(pdf_path)
        return data

    def chunk_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_max_length, len(text))
            if end < len(text):
                split_index = -1
                for ending in self.chunk_endings:
                    split_index = text.rfind(ending, start, end)
                    if split_index != -1:
                        split_index += len(ending) - 1
                        break
                if split_index == -1:
                    # If no breakpoint is found, force split at max length
                    split_index = end - 1
            else:
                split_index = end
            chunks.append(text[start:split_index + 1])
            start = split_index + 1
        return chunks
