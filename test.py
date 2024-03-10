import requests
from concurrent.futures import ThreadPoolExecutor

# service's URL
server_url = "http://localhost:9090"


def send_request(note_id):
    # define the context
    note_data = {
        "topic": f"test{note_id}",
        "name": f"note{note_id}",
        "text": f"This is test note number {note_id}"
    }

    # Send a POST request to the server to add notes
    response = requests.post(f"{server_url}/add_note", json=note_data)

    if response.status_code == 200:
        print(f"Note {note_id} added successfully.")
    else:
        print(f"Failed to add note {note_id}. Status code: {response.status_code}")


# Use ThreadPoolExecutor for concurrent execution
with ThreadPoolExecutor(max_workers=4) as executor:
    # Send 3 concurrent requests as an example
    executor.map(send_request, range(1, 5))
