# Tech Support Exercise

The exercise consists of two parts, they should be implemented as a script file written in **Ruby** by running:
`ruby code.rb load_data` for the **loading** part and `ruby code.rb analyze` for the **analyzing** part.

Before starting with the code, download, install and run a local MongoDB database that the script will connect to.

## Part 1: Loading dataset into a local MongoDB

1. Download the COVID "Cases and Deaths" dataset and store it in memory https://ourworldindata.org/explorers/covid using an HTTP Gem of your choice
2. Parse the CSV data and print the total lines to the console
3. Connect to the database using the standard MongoDB driver for Ruby
4. Inserting the parsed data to the DB

## Part 2: Analyzing the Data

The script should print the question followed by the answer in a line for all the questions below:

1. What's the number of records in the collection?
2. How many covid-19 cases are there in the dataset in total?
3. How many countries and continents does the dataset include?
4. What is the country with the highest total covid-19 cases per million in the dataset? Who is the lowest?
5. Where and when was the day with the highest number of new cases?
6. What is the country with the highest number of smokers (both females and males)?


## When done

Please send over the final `.rb` file along with a `.txt` file containing the console output when executing it.