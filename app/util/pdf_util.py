from io import BytesIO

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from io import StringIO
from pdfminer.pdfparser import PDFParser


class PDFUtil:

    def pdf_to_text(body):
        resource_manager = PDFResourceManager()
        fake_file_handle = StringIO()
        converter = TextConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(BytesIO(body), caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
        # close open handles
        converter.close()
        fake_file_handle.close()
        if text:
            return text

    def get_metadata(body):
        parser = PDFParser(BytesIO(body))
        doc = PDFDocument(parser)
        metadata = doc.info
        metadata['num_pages'] = PDFPage.get_pages(BytesIO(body))
        return metadata
