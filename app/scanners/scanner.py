# external modules
import importlib.resources
import json
from fastapi import UploadFile
from fuzzywuzzy import fuzz
# import requests
# import os
# import veryfi
# from veryfi.errors import BadRequest

# internal modules
from parsers import Parser


class Scanner:
    def __init__(self, file: UploadFile):
        self.success = False
        self.result = dict()
        self.file = file

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
        if loblaws_match > 70 or "loblaws" in scanned_merchant.lower():
            merchant = "Loblaws"
        if shoppers_match > 70 or "shoppers drug mart" in scanned_merchant.lower():
            merchant = "Shoppers Drug Mart"
        return merchant if merchant != '' else scanned_merchant
