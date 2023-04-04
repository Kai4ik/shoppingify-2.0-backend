
import requests
import json
import os
from typing import List
from ..queries.receipt.delete_receipt import delete_receipt_mutation
from ..queries.lineItems.delete_line_items import delete_line_items_mutation


def delete_receipt_and_related_line_items(receipt_number: int, username: str, line_items_ids: List[int]):
    r_value = {"success": False, "error_messages": []}
    variables = dict()
    for k in range(len(line_items_ids)):
        variables[f"input_{k}"] = dict()
        variables[f"input_{k}"]["id"] = line_items_ids[k]
    query = delete_line_items_mutation(line_items_ids)
    response = requests.post(os.getenv("pgql_url"), json={'query': query,
                                                                    'variables': variables})
    json_data = json.loads(response.text)
    if "errors" in json_data:
        for error in json_data["errors"]:
            r_value["error_messages"].append(error["message"])

    response = requests.post(os.getenv("pgql_url"), json={'query': delete_receipt_mutation,
                                                                    'variables': {"input": {"receiptNumber": receipt_number, "user": f'{username}'}}})

    json_data = json.loads(response.text)
    if "errors" in json_data:
        for error in json_data["errors"]:
            r_value["error_messages"].append(error["message"])
    else:
        r_value["success"] = True

    # No values were deleted in collection 'receipts' because no values you can delete were found matching these criteria.
    return r_value