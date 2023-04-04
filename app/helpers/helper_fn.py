import json
from moneyed import list_all_currencies, Currency


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def parse_receipt_data(data: str, user: str):
    deserialized_data = json.loads(data)
    parsed_data = dict()
    parsed_data["user"] = user
    line_items = []
    for key, value in deserialized_data.items():
        if key == 'merchant':
            parsed_data['merchant'] = value
        elif key == 'merchant_address':
            parsed_data['merchantAddress'] = value
        elif key == 'currency':
            parsed_data['currency'] = value
        elif key == 'payment_type':
            parsed_data['paymentType'] = value
        elif key == 'receiptNumber':
            parsed_data['receiptNumber'] = value
        elif key == 'purchaseDate':
            parsed_data['purchaseDate'] = value
        elif key == 'purchaseTime':
            parsed_data['purchaseTime'] = value
        elif key == 'subtotal':
            parsed_data['subtotal'] = float(value)
        elif key == 'tax':
            parsed_data['tax'] = float(value)
        elif key == 'total':
            parsed_data['total'] = float(value)

    for item in deserialized_data["initial_line_items"]:
        line_item = dict()
        item_id = item["id"]
        if "sku" in item:
            line_item["sku"] = str(item["sku"])
        line_item["itemTitle"] = deserialized_data[f'{item_id}']
        line_item["price"] = deserialized_data[f'{item_id}_price']
        line_item["qty"] = deserialized_data[f'{item_id}_qty']
        line_item["unit"] = deserialized_data[f'{item_id}_unit']
        line_item["total"] = deserialized_data[f'{item_id}_total']
        line_item["receiptNumber"] = parsed_data['receiptNumber']
        line_item["user"] = user
        line_items.append(line_item)

    parsed_data["numberOfItems"] = len(line_items)
    parsed_data["lineItems"] = line_items
    return parsed_data


def validate_data(data: dict):
    errors: [str] = []
    list_of_currencies = list_all_currencies()
    list_of_merchants = list_all_merchants()
    list_of_units = list_all_units()

    if Currency(data["currency"]) not in list_of_currencies:
        errors.append("Not a valid currency")
    if data["merchant"].lower() not in list_of_merchants:
        errors.append("Not a valid merchant")
    if type(data["receiptNumber"]) is not int:
        errors.append("Receipt number should only contain numeric characters")
    if round((data["subtotal"] + data["tax"]), 2) != data["total"]:
        errors.append("Total should be equal to sum of subtotal and tax")

    for item in data["lineItems"]:
        if round((item["price"] * item["qty"]), 2) != item["total"]:
            errors.append(f'{item["itemTitle"]}: {item["total"]} != {round((item["price"] * item["qty"]), 2)}')
        if item["unit"] not in list_of_units:
            errors.append("Not a valid unit")

    return {"validation_failed": True, "errors": errors} if len(errors) > 0 else {"validation_failed": False}


def list_all_merchants():
    return ["loblaws", "shoppers drug mart"]


def list_all_units():
    return ["kg", "ea"]
