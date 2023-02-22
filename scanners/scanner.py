import importlib.resources
import json
import os
import veryfi
from veryfi.errors import BadRequest
from fastapi import UploadFile
from parsers import Parser
from fuzzywuzzy import fuzz
# import requests


class Scanner:
    def __init__(self, file: UploadFile):
        self.success = False
        self.result = dict()
        self.file = file

    def scan_via_asprise(self, file: UploadFile):
        pass
        '''
        ocr_endpoint = 'https://ocr.asprise.com/api/v1/receipt'
        result = requests.post(ocr_endpoint, data={
            'api_key': 'TEST',
            'recognizer': 'US',  # can be 'US', 'CA', 'JP', 'SG' or 'auto' \
            'ref_no': 'ocr_python_123',
        },  files={"file": self.file.file.read()})
        print(result.json())
        '''

    def scan_via_veryfi(self, file: UploadFile):
        '''
        client_id = os.getenv("veryfi_client_id")
        client_secret = os.getenv("veryfi_client_secret")
        username = os.getenv("veryfi_username")
        api_key = os.getenv("veryfi_api_key")

        client = veryfi.Client(client_id, client_secret, username, api_key)
        try:
            data = client.process_document(file)
            // TODO: 48-63 go here
        except BadRequest as err:
            self.result["error_message"] = err.split(",")[-1].strip()
        '''

        with importlib.resources.open_text("scanners", "data.json") as json_file:
            data = json.load(json_file)

        scanned_merchant = data["vendor"]["name"]
        merchant = self.merchant_matching(scanned_merchant)
        self.result["merchant"] = merchant
        self.result["merchant_address"] = data["vendor"]["address"].replace("\n", " ")
        self.result["tax"] = float(data["tax"]) if data["tax"] else 0
        self.result["subtotal"] = float(data["subtotal"])
        self.result["total"] = float(data["total"])
        self.result["currency"] = data["currency_code"] if data["currency_code"] else "CAD"
        self.result["purchase_date"] = data["date"]
        self.result["payment_type"] = data["payment"]["type"]
        self.result["receipt_number"] = data["invoice_number"]

        ocr_text = data["ocr_text"]
        parser = Parser("veryfi", ocr_text, merchant)
        self.result["line_items"] = parser.fetch_data()
        self.success = True
        return self.result, self.success

    @staticmethod
    def merchant_matching(scanned_merchant: str) -> str:
        merchant: str = ''
        loblaws_match = fuzz.ratio(scanned_merchant.lower(), "loblaws")
        shoppers_match = fuzz.ratio(scanned_merchant.lower(), "shoppers drug mart")
        if loblaws_match > 70:
            merchant = "Loblaws"
        if shoppers_match > 70:
            merchant = "Shoppers Drug Mart"
        return merchant if merchant != '' else scanned_merchant
