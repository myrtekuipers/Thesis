import requests
import json

# API endpoint for obtaining a bearer token
token_url = "https://api.thuisarts.nl/oauth/token"

# Replace with your client credentials
client_id = "CFfdGB4cUO5pG8ZNjdZIW0_JjwOJKUEtWOl837vvass"
client_secret = "80z_ZJBXy_6sLpGHwWOinQ"

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
    api_url_base = "https://api.thuisarts.nl/v/1/situations?_format=json&page="
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # List to store all situations
    all_situations = []

    # Loop through all pages (16 in this case)
    for i in range(1, 17):  # Pages are 1-indexed
        api_url = f"{api_url_base}{i}"
        api_response = requests.get(api_url, headers=headers)

        # Check the response from the API
        if api_response.status_code == 200:
            print(f"Processing data from page {i}")
            page_data = api_response.json()

            # Extract situations from the current page and append to the list
            all_situations.extend(page_data.get('situations', []))

        else:
            print(f"Error from API on page {i}: {api_response.status_code}")
            print(api_response.text)

    # Save all situations to a single JSON file
    with open('data/all_situations.json', 'w') as f:
        json.dump(all_situations, f)

else:
    print(f"Error obtaining bearer token: {token_response.status_code}")
    print(token_response.text)
