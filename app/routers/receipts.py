# external modules
from fastapi import APIRouter, File, UploadFile, Form, Depends, Request, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import json
import jwt
import os
import requests

# internal modules
from scanners import Scanner
from helpers import save_receipt_to_s3, parse_receipt_data, validate_data, create_receipt, create_line_items, delete_receipt_and_related_line_items


def verify_token(request: Request) -> bool:
    token = request.headers.get("Authorization").split(" ")[-1]
    token_kid = jwt.get_unverified_header(token)
    cognito_issuer = f'https://cognito-idp.{os.getenv("aws_region")}.amazonaws.com/{os.getenv("user_pool_id")}/.well-known/jwks.json'
    jwks = requests.get(cognito_issuer).json()
    key = None
    for jwk in jwks["keys"]:
        if jwk["kid"] == token_kid["kid"]:
            key = jwt.get_algorithm_by_name("RS256").from_jwk(json.dumps(jwk))

    if key is not None:
        try:
            decoded_token = jwt.decode(token, key, algorithms=["RS256"], audience=os.getenv("user_pool_client_id"))
            request.state.email = decoded_token["email"]
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidAudienceError,
                jwt.exceptions.InvalidTokenError) as e:
            raise HTTPException(status_code=401, detail="Token verification failed")




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(dependencies=[Depends(verify_token), Depends(oauth2_scheme)])


@router.post("/scanReceipt", tags=["receipts"])
def scan_receipt(file: UploadFile = File(...)):
    r_value = {"success": False, "data": [], "error_message": ""}
    scanner = Scanner(file)
    result, success = scanner.scan_via_veryfi(file)
    if success is True:
        r_value["success"] = True
        r_value["data"] = result
    else:
        if result["error_message"] == "You have reached your scan limit please contact support@veryfi.com to upgrade your account.":
            message = "Unfortunately receipt can't be scanned because monthly scan limit was reached for Kai's account"
            r_value["error_message"] = message
    return r_value


@router.post("/saveReceipt", tags=["receipts"])
def save_receipt(request: Request, data: str = Form(), file: UploadFile = File(...), ):
    # TODO: better error messages
    r_value = {"success": False,  "error_messages": []}
    parsed_data = parse_receipt_data(data, request.state.email)
    validation_result = validate_data(parsed_data)
    if validation_result["validation_failed"] is False:
        response = create_receipt(parsed_data)
        if response["success"]:
            response = create_line_items(parsed_data["lineItems"])
            if response["success"] is False:
                r_value["error_messages"] = response["error_messages"]
            else:
                save_receipt_to_s3(request.state.email, parsed_data["receiptNumber"], file)
                r_value["success"] = True
        else:
            r_value["error_messages"] = response["error_messages"]

    else:
        r_value["error_messages"] = validation_result["errors"]

    return r_value


class DeleteReceiptProps(BaseModel):
    receipt_number: int
    line_items_ids: List[int]


@router.post("/deleteReceipt", tags=["receipts"])
def delete_receipt(request: Request, props: DeleteReceiptProps):
    r_value = {"success": False,  "error_messages": []}
    response = delete_receipt_and_related_line_items(props.receipt_number, request.state.email, props.line_items_ids)
    if response["success"]:
        r_value["success"] = True
    else:
        r_value["error_messages"] = response["error_messages"]
    return r_value


