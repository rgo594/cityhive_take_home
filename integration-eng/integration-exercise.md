# Inventory Digestion Exercise

The exercise is divided to two main pieces:

1.    Inventory data extraction and transformation - written in Python (see `integration-exercise.py` as entry point)
2.    Inventory data storage and validation API - written in Ruby on Rails

## Note

1. Rather than using pandas/numpy, use Python's builtin packages.
2. The `.py` script uses `csv.reader`, you should probably switch it to `DictReader`.

## Extraction and Transformation
1.  Make a GET request to Amazon S3 with the details from the python script and save the
    content into a file locally: https://docs.aws.amazon.com/AmazonS3/latest/userguide/RESTAPI.html
2.  The script outputs the content to the console, change it so that the output
    will be written to a CSV file.
3.  Add a department column to the export, there's a column in the import that
    contains that information.
4.  If the UPC column contains something other than a string of numbers at a
    length that is greater than 5, we'd want to instead, leave that column blank
    in the export, and populate a column called "internal_id" that will contain
    the ID of the record from the original file prefixed by "biz_id_".
5.  Increase the price by 7% if the original has more than 30% margin over the
    cost, otherwise increase the price by 9%. Round the final result to the 2nd
    decimal point.
6.  Add a name column to the output that is a concatenation of the item and
    itemextra columns
7.  The output should only contain item that were sold during 2020
8.  Add a properties column to the output that will contain a JSON of a dict
    containing the department, vendor and description
9.  Add a tags field to the output that will contain the following tags:
    * `duplicate_sku` if the input file contains the same ItemNum for multiple rows.
    * `high_margin` if the margin on the item is more than 30%
    * `low_margin` if the margin on the item is less than 30%
10. Instead of saving the file locally and then parsing it, add another flow to the script that passes the downloaded content directly to the CSV parser.

## Storage and Validation API

1. Create a new Ruby on Rails API project that uses the `Mongoid` gem as the ORM module instead of `ActiveRecord`
2. The app should have a single model in it - the `InventoryUnit` model that represent a single row of inventory data along with information that will be relevant for record keeping: 
    * Creation time of the record
    * Batch identifier that is shared between all items created as part of the same API call
3. Expose two endpoints:
    * `POST inventory_uploads.json` that receives a parsed JSON from the python code and creates InventoryUnits from it
    * `GET inventory_uploads.json` that will return a JSON where each element is has:
        * `batch_id` the shared ID between all the inventory units created by the same API call
        * `number_of_units` the total number of units in that batch
        * `average_price` the average price of the units
        * `total_quantity` the sum of all quantities across the inventory units in that batch
4. Update the python code such that it receives one of 3 inputs: 
    * `generate_csv` will generate the CSV file with the parsed data
    * `upload` will upload the parsed data as a JSON array to the API
    * `list_uploads` will call the inventory_uploads listing endpoint and print the result
    