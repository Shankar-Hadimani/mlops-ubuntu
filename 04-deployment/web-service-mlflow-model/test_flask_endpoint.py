import requests


url = 'http://127.0.0.1:9696/predict'
ride_data = {
    "PULocationID":10,
    "DOLocationID":40,
    "trip_distance":50
}

response = requests.post(url=url, json=ride_data)
print(response.json())