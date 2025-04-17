import requests

url = "http://localhost:3000/inventory_uploads.json"

payload = {
    "inventory_units": [
        { "price": 13.0, "quantity": 2 },
        { "price": 9.5, "quantity": 7 },
        { "price": 3.0,  "quantity": 1 }
    ]
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())