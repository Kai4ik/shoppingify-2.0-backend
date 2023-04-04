import requests
import json
import os
from ..queries.receipt.create_receipt import create_receipt_mutation


def create_receipt(data: dict):
    r_value = {"success": False, "error_messages": []}
    variables = dict()
    for key, value in data.items():
        if key != "lineItems":
            variables[key] = value

    response = requests.post(os.getenv("pgql_url"), json={'query': create_receipt_mutation,
                                                                    'variables': {"input": {"receipt": variables}}})
    json_data = json.loads(response.text)
    if "errors" in json_data:
        for error in json_data["errors"]:
            r_value["error_messages"].append(error["message"])
    else:
        r_value["success"] = True

    return r_value
