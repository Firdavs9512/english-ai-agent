from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import io


class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)

    def extract_text_from_pages(self, start_page: int, end_page: int) -> str:
        """
        Extract text from specified page range
        """
        text = ""
        for page_num in range(start_page - 1, end_page):
            if page_num < len(self.reader.pages):
                page = self.reader.pages[page_num]
                text += page.extract_text()
        return text

    def get_total_pages(self) -> int:
        """
        Get total number of pages in PDF
        """
        return len(self.reader.pages)

    def convert_pdf_to_images(self) -> list:
        """
        PDF faylni rasmlar ro'yxatiga o'tkazish
        
        Returns:
            list: PNG formatidagi rasmlar ro'yxati (bytes)
        """
        # PDF faylni rasmlarga o'tkazish
        images = convert_from_path(self.pdf_path)
        
        # Har bir rasmni PNG formatiga o'tkazish
        png_images = []
        for image in images:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            png_images.append(img_byte_arr.getvalue())
            
        return png_images

    def extract_pages(self, start_page: int, end_page: int) -> str:
        """
        Yuklangan pdf ichidan berilgan sahifalar yordamida yangi pdf fayl yaratish
        va yangi yaratilgan pdf fayl nomini qaytarish
        """
        # Create a new PDF writer
        new_pdf_writer = PdfWriter()

        # Add pages from the original PDF to the new PDF
        for page_num in range(start_page - 1, end_page):
            if page_num < len(self.reader.pages):
                page = self.reader.pages[page_num]
                new_pdf_writer.add_page(page)

        # Create a new PDF file
        new_pdf_path = f"extracted_pages_{start_page}_{end_page}.pdf"
        with open(new_pdf_path, "wb") as new_pdf_file:
            new_pdf_writer.write(new_pdf_file)

        return new_pdf_path


# Example testing
# if __name__ == "__main__":
#     pdf_processor = PDFProcessor("A1.pdf")
#     new_pdf_path = pdf_processor.extract_pages(46, 63)
#     print(new_pdf_path)
