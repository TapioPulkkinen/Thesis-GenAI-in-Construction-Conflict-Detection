import fitz
import io
from docx import Document


class FileReader:

    def read_file(self, file):
        if 'text' in file.type:
            return self.read_txt_file(file)
        elif 'pdf' in file.type:
            return self.read_pdf_file(file)
        elif 'document' in file.type:
            return self.read_docx_file(file)
        else:
            raise ValueError("Unsupported file type")

    def read_txt_file(self, file):
        # Assuming the uploaded file is a text file, read it directly.
        return file.getvalue().decode('utf-8')

    def read_pdf_file(self, file):
        text = ''
        # Convert Streamlit UploadedFile to a seekable bytes stream for PyMuPDF
        pdf_bytes = io.BytesIO(file.getvalue())
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def read_docx_file(self, file):
        # Convert Streamlit UploadedFile to a seekable bytes stream for python-docx
        docx_bytes = io.BytesIO(file.getvalue())
        doc = Document(docx_bytes)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        return text
