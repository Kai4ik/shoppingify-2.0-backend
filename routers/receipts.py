from fastapi import APIRouter, File, UploadFile
from scanners import Scanner

router = APIRouter()


@router.post("/scanReceipt", tags=["receipts"])
def scan_receipt(file: UploadFile = File(...)):
    response = {"success": False, "data": [], "error_message": ""}
    scanner = Scanner(file)
    result, success = scanner.scan_via_veryfi(file)
    if success is True:
        response["success"] = True
        response["data"] = result
    else:
        if result["error_message"] == "You have reached your scan limit please contact support@veryfi.com to upgrade your account.":
            message = "Unfortunately receipt can't be scanned because monthly scan limit was reached for Kai's account"
            response["error_message"] = message
    return response


