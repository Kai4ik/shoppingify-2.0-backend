import requests
import json
from .gq_queries import create_receipt_mutation, create_line_items_mutation


def create_receipt(data: dict):
    r_value = {"success": False, "error_messages": []}
    variables = dict()
    for key, value in data.items():
        if key != "lineItems":
            variables[key] = value

    response = requests.post("http://localhost:5000/graphql", json={'query': create_receipt_mutation,
                                                                    'variables': {"input": {"receipt": variables}}})
    json_data = json.loads(response.text)
    if "errors" in json_data:
        for error in json_data["errors"]:
            r_value["error_messages"].append(error["message"])
    else:
        r_value["success"] = True

    return r_value


def create_line_items(line_items: [dict]):
    r_value = {"success": False, "error_messages": []}
    variables = dict()
    for k in range(len(line_items)):
        variables[f"input_{k}"] = dict()
        variables[f"input_{k}"]["lineItem"] = line_items[k]

    query = create_line_items_mutation(line_items)
    response = requests.post("http://localhost:5000/graphql", json={'query': query,
                                                                    'variables': variables})
    json_data = json.loads(response.text)
    if "errors" in json_data:
        for error in json_data["errors"]:
            r_value["error_messages"].append(error["message"])
    else:
        r_value["success"] = True

    return r_value

