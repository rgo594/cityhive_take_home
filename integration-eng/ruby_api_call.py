import requests

url = "http://localhost:3000/inventory_uploads.json"

payload = {
    "inventory_units": [
        { "price": 10.0, "quantity": 2 },
        { "price": 12.5, "quantity": 5 },
        { "price": 8.0,  "quantity": 3 }
    ]
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())