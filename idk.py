import csv
import requests
import json
import os
import re
from io import StringIO
from typing import List, Dict, Tuple, Optional
from datetime import datetime


def calculate_price_increase(price: float, margin: float) -> float:
    if margin > 0.3:
        new_price = price * 1.07
    else:
        new_price = price * 1.09
    return round(new_price, 2)


def determine_upc_or_internal_id(upc: str, row_id: str) -> Tuple[Optional[str], Optional[str]]:
    if len(upc) > 5 and not re.fullmatch(r"\d+", upc):
        return None, f"biz_id_{row_id}"
    return upc, None


def extract_fields_from_row(row: List[str]) -> Dict:
    return {
        "upc_raw": row[0],
        "item": row[1],
        "cost": float(row[3]),
        "price": float(row[4]),
        "quantity": row[5],
        "vendor_number": row[12],
        "department": row[13],
        "item_extra": row[36],
        "last_sold": row[46],
        "row_id": row[90],
        "description": row[142],
    }


def process_line(row: List[str], item_num_duplicates: set) -> Optional[Dict]:
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
        print("Error processing row:", row)
        raise


def skip_line(row: List[str], line_num: int) -> bool:
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


def write_to_csv():
    bucket = "cityhive-stores"
    key = "_utils/inventory_export_sample_exercise.csv"
    url = f"https://{bucket}.s3.amazonaws.com/{key}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch S3 file")

    working_directory = os.path.dirname(os.path.abspath(__file__))
    local_file_path = f"{working_directory}/inventory_export_sample_exercise.csv"

    csv_file = StringIO(response.text)
    reader = csv.reader(csv_file, delimiter='|')

    lines = [{"row": row, "line_num": reader.line_num} for row in reader]

    with open(local_file_path, 'w+') as out_file:
        item_num_duplicates = fetch_item_num_duplicates(lines)

        for line in lines:
            row = line["row"]
            line_num = line["line_num"]

            if skip_line(row, line_num):
                continue

            processed = process_line(row, item_num_duplicates)
            if processed:
                out_file.write(json.dumps(processed) + "\n")


if __name__ == "__main__":
    write_to_csv()