import requests
import json

# API endpoint for obtaining a bearer token
token_url = "https://api.thuisarts.nl/oauth/token"

# Replace with your client credentials
client_id = "CFfdGB4cUO5pG8ZNjdZIW0_JjwOJKUEtWOl837vvass"
client_secret = "IJIqpOWP60Ypb6oWLd8wIg"

# Replace with the actual scope required by the API
scope = "api"

# Data to be sent in the POST request to obtain the token
token_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': scope
}

# Make the POST request to obtain the bearer token
token_response = requests.post(token_url, data=token_data)

# Check if the request was successful (status code 200)
if token_response.status_code == 200:
    # Parse the response to get the access token
    access_token = token_response.json().get('access_token')

    # Use the obtained access token in subsequent requests
    api_url = "https://api.thuisarts.nl/v/1/situations?_format=json"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Make a GET request to the API using the obtained bearer token
    api_response = requests.get(api_url, headers=headers)

    # Check the response from the API
    if api_response.status_code == 200:
        print(api_response.json())
    else:
        print(f"Error from API: {api_response.status_code}")
        print(api_response.text)

else:
    print(f"Error obtaining bearer token: {token_response.status_code}")
    print(token_response.text)

#save the json file
with open('data.json', 'w') as f:
    json.dump(api_response.json(), f)

