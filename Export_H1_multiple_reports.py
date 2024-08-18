# Export bulk hackerone reports in file with report id
# Add Cookie in this code
# Run code
# Enter multiple reports id and then type "done"
# Vulnerability_informstion saved in FILENAME.txt

import requests

# Function to prompt the user for IDs
def get_ids():
    ids = []
    print("Please enter the IDs, one per line. Type 'done' when finished:")
    while True:
        id_input = input("> ")
        if id_input.lower() == 'done':
            break
        ids.append(id_input)
    return ids

# Get the list of IDs from the user
ids = get_ids()

# Define the headers based on your provided request details
headers = {
    'Cookie': '' 
}

# Open the file in write mode
with open('FILENAME1.txt', 'w') as file:
    # Iterate over the list of IDs provided by the user
    for id in ids:
        # Construct the URL with the current ID
        url = f"https://hackerone.com/reports/{id}.json"

        # Send the GET request
        response = requests.get(url, headers=headers)

        # Ensure the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            json_response = response.json()

            # Extract the specific JSON value you're interested in
            # Modify 'desired_key' to the key you need from the JSON response
            specific_value = json_response.get('vulnerability_information')

            # Write the result to the file
            file.write(f"ID: {id} - Value: {specific_value}\n")
        else:
            # Write the failure message to the file
            file.write(f"Failed to retrieve data for ID: {id}, Status Code: {response.status_code}\n")