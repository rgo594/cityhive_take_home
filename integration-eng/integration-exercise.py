import csv
import requests
import json
import os
import re
from io import StringIO
from typing import List, Dict
from datetime import datetime
from sys import argv, exit

def calculate_price_increase(price: float, margin: float) -> float:
    if margin > 0.3:
        new_price = price * 1.07
    else:
        new_price = price * 1.09
    return round(new_price, 2)


def determine_upc_or_internal_id(upc: str, row_id: str):
    if len(upc) > 5 and not re.fullmatch(r"\d+", upc):
        return None, f"biz_id_{row_id}"
    return upc, None


def extract_fields_from_row(row: List) -> Dict:
    return {
        "upc_raw": row[0],
        "item": row[1],
        "cost": float(row[3]),
        "price": float(row[4]),
        "quantity": row[191],
        "vendor_number": row[12],
        "department": row[13],
        "item_extra": row[36],
        "last_sold": row[46],
        "row_id": row[90],
        "description": row[142],
    }


def process_line(row: List, item_num_duplicates: set) -> Dict:
    try:
        fields = extract_fields_from_row(row)
        if fields["last_sold"] == "NULL" or not fields["last_sold"]:
            return None

        last_sold_dt = datetime.strptime(fields["last_sold"], "%Y-%m-%d %H:%M:%S.%f")
        if not (datetime(2020, 1, 1) <= last_sold_dt < datetime(2021, 1, 1)):
            return None

        upc, internal_id = determine_upc_or_internal_id(fields["upc_raw"], fields["row_id"])
        margin = 0 if fields["price"] == 0 else (fields["price"] - fields["cost"]) / fields["price"]

        tags = []
        if fields["upc_raw"] in item_num_duplicates:
            tags.append("duplicate_sku")
        if margin > 0.3:
            tags.append("high_margin")
        elif margin < 0.3:
            tags.append("low_margin")

        return {
            "upc": upc,
            "internal_id": internal_id,
            "price": calculate_price_increase(fields["price"], margin),
            "quantity": fields["quantity"],
            "department": fields["department"],
            "name": f"{fields['item']} {fields['item_extra']}".replace("NULL", "").strip(),
            "properties": {
                "department": fields["department"],
                "vendor": fields["vendor_number"],
                "description": fields["description"]
            },
            "tags": tags,
            "last_sold": last_sold_dt.strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(row)
        raise


def skip_line(row: List, line_num: int) -> bool:
    return len(row) <= 10 or line_num in {0, 1, 2}


def fetch_item_num_duplicates(lines: List[Dict]) -> set:
    item_nums = set()
    item_duplicates = set()

    for line in lines:
        row = line["row"]
        line_num = line["line_num"]

        if skip_line(row, line_num):
            continue

        item_num = row[0]
        if item_num in item_nums:
            item_duplicates.add(item_num)
        else:
            item_nums.add(item_num)

    return item_duplicates

def generate_csv(lines : List, file_path):
    for row in lines:
        if "properties" in row and isinstance(row["properties"], dict):
            row["properties"] = json.dumps(row["properties"])
        if "tags" in row and isinstance(row["tags"], list):
            row["tags"] = ",".join(row["tags"])

    fieldnames = sorted({key for row in lines for key in row.keys()})

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lines)

def upload(lines : List):
    url = "http://localhost:3000/inventory_uploads.json"

    payload = {
        "inventory_units": lines
    }

    response = requests.post(url, json=payload)

    print(response.status_code)
    print(response.json())


def list_uploads():
    url = "http://localhost:3000/inventory_uploads.json"

    response = requests.get(url)

    print(response.json())

def parse_lines():
    bucket = "cityhive-stores"
    key = "_utils/inventory_export_sample_exercise.csv"
    url = f"https://{bucket}.s3.amazonaws.com/{key}"


    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch S3 file")

    csv_file = StringIO(response.text)
    reader = csv.reader(csv_file, delimiter='|')

    input_lines = [{"row": row, "line_num": reader.line_num} for row in reader]

    # with open(local_file_path, 'w+') as out_file:

    item_num_duplicates = fetch_item_num_duplicates(input_lines)

    output_lines : List = []
    for line in input_lines:
        row = line["row"]
        line_num = line["line_num"]

        if skip_line(row, line_num):
            continue

        processed = process_line(row, item_num_duplicates)
        if processed:
            output_lines.append(processed)

    return output_lines



if(argv[1] == "generate_csv"):
    working_directory = os.path.dirname(os.path.abspath(__file__))
    local_file_path = f"{working_directory}/inventory_export_sample_exercise.csv"

    output_lines = parse_lines()
    generate_csv(lines=output_lines, file_path=local_file_path)

elif(argv[1] == "upload"):
    output_lines = parse_lines()
    upload(lines=output_lines)

elif(argv[1] == "list_uploads"):
    list_uploads()


        # row = line["row"]
        # colnames = [
        #     "upc_raw"
        #     ,"item"
        #     ,"cost"
        #     ,"price"
        #     ,"quantity"
        #     ,"vendor_number"
        #     ,"department"
        #     ,"item_extra"
        #     ,"last_sold"
        #     ,"row_id"
        #     ,"description"
        # ]
        # for i in range(len(row)):
        #     header = row[i].lower()
        #     if "cost" in header:
        #         print(i, " ", header)
        # # print(row)
        # # print(row.index(row[-1]))
        # exit()