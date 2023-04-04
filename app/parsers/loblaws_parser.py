# external modules
import re
from datetime import datetime
import hashlib
import json

# internal modules
from helpers import isfloat


class LoblawsParser:
    def __init__(self, ocr_lib: str, ocr_text: str,):
        self.result = []
        self.ocr_lib = ocr_lib
        self.ocr_text = ocr_text

    def fetch_data(self):
        if self.ocr_lib == "asprise":
            pass
        elif self.ocr_lib == "veryfi":
            sku, total, product_price, qty, product_title = None, None, None, None, None
            text_split = self.ocr_text.split("\n")

            for k in range(len(text_split)):
                line = text_split[k]
                line = line.replace("/", " ").replace("*", " ").replace(":", "").strip()
                remove_parentheses = re.findall(r"\(\d*\)", line)
                if len(remove_parentheses) > 0:
                    line = line.replace(remove_parentheses[0], "").strip()

                if_or = re.findall(r"or\s\d", line)
                if len(if_or) > 0:
                    line = line.split("or", 1)[0]

                if "RECORD" in line or "TRANSACTION" in line:
                    break

                category = re.findall(r"\d\d-[a-zA-Z]", line)
                categories = ["GROCERY", "PRODUCE", "HOME", "DAIRY", "MEATS", "SEAFOOD", "BAKERY INSTORE",
                              "NATURAL FOODS", "DELI", "BULK FOOD", "SALAD BAR", "BAKERY COMMERCIAL"]
                category_double_check = any(category in line for category in categories)

                if len(category) == 0 and category_double_check is False:
                    line = line.replace("-", "")
                    if len(line.split()) > 0 and line.split()[0].isnumeric() and "$" not in line:
                        sku = line.split()[0]
                        line = line.replace(sku, "")

                        price = re.findall(r"\d+\.\d+|\d+,\d+", line)
                        if len(price) > 0:
                            total, product_price = price[0], price[0]
                            line = line.replace(total, "")

                        line = line.strip()

                        if line.split("\t")[0] != "ea":
                            filter_regex = re.compile(
                                "|".join(map(re.escape, ["HRJ", "MAJ", "MRJ", "HAJ", "HMR", "HMRJ", "MR.J"]))
                            )
                            line = filter_regex.sub("", line).strip()
                            product_title = line.split("\t")[0]
                    else:
                        price_per_product = re.findall(r"\$\d*\.\d\d|\$\d*,\d\d", line)

                        if len(price_per_product) > 0:
                            product_price = price_per_product[0].replace("$", "")

                        if isfloat(line.split("\t")[-1].replace(",", ".")):
                            total = line.split("\t")[-1].replace(",", ".")

                    if total is None:
                        next_line = text_split[k + 1].split()
                        price = re.findall(r"\d+\.\d+|\d+,\d+", text_split[k + 1])
                        if len(next_line) > 1 and len(price) > 0 and "$" not in text_split[k + 1]:
                            total = price[0]
                            if product_price is None:
                                product_price = price[0]
                            text_split[k + 1] = text_split[k + 1].replace(total, "")

                    if product_title == '':
                        sku = None

                    if None not in (total, sku, product_title, product_price):
                        formatted_product_price = round(float(product_price.replace(",", ".")), 2)
                        formatted_total = round(float(total.replace(",", ".")), 2)

                        product = {
                            "sku": sku,
                            "price": formatted_product_price,
                            "productTitle": product_title,
                            "total": formatted_total,
                            "unit": "ea",
                            "qty": int(formatted_total / formatted_product_price)
                        }
                        dhash = hashlib.md5()
                        dhash.update(json.dumps([product, datetime.now().timestamp()], sort_keys=True).encode())
                        p_id = dhash.hexdigest()
                        product["id"] = p_id
                        if product_price != total:
                            qty = formatted_total / formatted_product_price
                            if qty.is_integer() is False:
                                product["qty"] = round(formatted_total / formatted_product_price, 3)
                                product["unit"] = "kg"

                        if formatted_product_price > 35 or formatted_total > 35:
                            product["payAttention"] = True

                        self.result.append(product)
                        sku, total, product_price, qty, product_title = None, None, None, None, None

        return self.result
