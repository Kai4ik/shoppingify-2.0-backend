from .loblaws_parser import LoblawsParser


class Parser:
    def __init__(self, ocr_lib: str, ocr_text: str, merchant: str):
        self.result = []
        self.ocr_lib = ocr_lib
        self.merchant = merchant.lower()
        self.ocr_text = ocr_text

    def fetch_data(self):
        if self.merchant.lower() == "loblaws":
            processor = LoblawsParser(self.ocr_lib, self.ocr_text)
            self.result = processor.fetch_data()

        return self.result
