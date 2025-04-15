import csv
import requests
from sys import exit
import json
import os
from bs4 import BeautifulSoup
import re
from io import StringIO
from typing import List

from datetime import datetime

#import "./integrations-entryfile.html"

# 1. Using requests or any other HTTP library, grab the file HTML from: https://bitbucket.org/cityhive/jobs/src/master/integration-eng/integration-entryfile.html 
# 2. Then, parse the URL for the csv file located in the S3 bucket (as part of the script, not by hand)
# 3. Make a GET request to Amazon's S3 with the details from #2 and save the to `local_file_path`
# initial_html_file="https://bitbucket.org/cityhive/jobs/src/master/integration-eng/integration-entryfile.html"
# parser = MyHTMLParser()

# response = requests.get(url=initial_html_file)

def calculate_price_increase(price : float, margin : float):
  if(margin > .3):
    new_price = price * 1.07
  else:
    new_price = price * 1.09
  
  return round(new_price, 2)

def determine_upc_or_internal_id(upc : str, row_id : int):
  if len(upc) > 5 and not re.fullmatch(r"\d+", upc):
    internal_id = "biz_id_" + row_id
    upc = None 
  else:
    internal_id = None

  return upc, internal_id

def process_line(row : List, item_num_duplicates):
  try:
    last_sold = row[46]
    if last_sold == "NULL" or last_sold is None:
      return
    else:
      last_sold_dt : datetime = datetime.strptime(last_sold, "%Y-%m-%d %H:%M:%S.%f")

      if not (last_sold_dt >= datetime(2020, 1, 1, 0, 0, 0) and last_sold_dt < datetime(2021, 1, 1, 0, 0, 0)):
        return
      
    upc, internal_id = determine_upc_or_internal_id(row[0], row[90])
    price = float(row[4])    
    cost = float(row[3])
    item = row[1]
    item_extra = row[36]
    quantity = row[5]
    department = row[13]
    description = row[142]
    vendor_number = row[12]
    item_num = row[0]
    properties = {'department' : department, 'vendor' : vendor_number, 'description' : description}
    margin = 0 if price == 0 else (price - cost) / price
    tags = []

    if(item_num in item_num_duplicates):
      tags.append("duplicate_sku")
    if(margin > 0.3):
      tags.append("high_margin")
    elif(margin < 0.3):
      tags.append("low_margin")

    row = {
      'upc': upc,
      'price': calculate_price_increase(price=price, margin=margin),
      'quantity': quantity,
      'department' : department,
      'internal_id' : internal_id,
      #I assume null values shouldn't be concatenated
      'name' : (item + " " + item_extra).replace("NULL", "").strip(),
      'properties' : properties,
      'tags' : tags,
      'last_sold': last_sold
    }
    return row
  except Exception as e:
    print(row)
    raise
  
def skip_line(row, line_num):
    if not (len(row) > 10):
      return True
    elif line_num in [0, 1, 2]:
      return True
    else:
      return False

def fetch_item_num_duplicates(lines : List):
  item_nums = set()
  item_duplicates = set()

  for line in lines:
    row = line["row"]
    line_num = line["line_num"]

    if(skip_line(row, line_num)):
      continue
    
    item_num = row[0]
    if(item_num not in item_nums):
      item_nums.add(item_num)
    else:
      item_duplicates.add(item_num)
  
  return item_duplicates


def write_to_csv():
  bucket : str = "cityhive-stores"
  key : str = "_utils/inventory_export_sample_exercise.csv"
  "us-west-2"

  url = f"https://{bucket}.s3.amazonaws.com/{key}"
  response = requests.get(url)

  working_directory = os.path.dirname(os.path.abspath(__file__))

  local_file_path : str = f"{working_directory}/inventory_export_sample_exercise.json"

  csv_file = StringIO(response.text)

  lines = []
  reader = csv.reader(csv_file, delimiter='|')
  for line in reader:
    lines.append({"row" : line, "line_num" : reader.line_num})

  with open(local_file_path, 'w+') as in_file:
    item_num_duplicates = fetch_item_num_duplicates(lines=lines)
    for line in lines:
      row = line["row"]
      line_num = line["line_num"]

      #skipping header rows.
      if(skip_line(row=row, line_num=line_num)):
        continue

      l = process_line(row=row, item_num_duplicates=item_num_duplicates)
      if l: in_file.write(json.dumps(l) + "\n")

write_to_csv()