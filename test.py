import requests

url = "http://127.0.0.1:8000/upload"

files = {"image": open("src\\dataset\\Jithu Tagore\\WIN_20260309_10_38_35_Pro.jpg", "rb")}

response = requests.post(url, files=files)

print(response.json())