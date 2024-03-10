import requests

# Server URL to send requests to.
server_url = "http://localhost:9090"


def send_request(method, url, **kwargs):
    #  Sends a request to the server.
    #  'method' is the type of HTTP request (like 'GET' or 'POST').
    # 'url' is the address where the request is sent.
    # '**kwargs' are additional parameters that can be passed, like data in 'json'.
    try:
        # Try to send the request to the server.
        response = requests.request(method, url, **kwargs)
        # Check the response. If it's an error (like 404 or 500), this will raise an error.
        response.raise_for_status()
        return response  # Return the response if everything is okay.
    except requests.RequestException as e:
        # If there's a problem with the request, print the error.
        print(f"Request error: {e}")
        return None  # Return 'None' to indicate the request failed.


def add_note():  # Collects data for a new note from the user and sends it to the server.
    # Get inputs from the user.
    topic = input("Enter the topic: ")
    name = input("Enter the note's name: ")
    text = input("Enter the text of the note: ")
    # Send the data to the server.
    response = send_request('POST', f"{server_url}/add_note", json={'topic': topic, 'name': name, 'text': text})
    # If the server responded successfully, print the response.
    if response:
        print(response.json())
    else:
        # If the request failed, let the user know.
        print("Failed to add note due to a request error.")


def get_notes():  # Asks for a topic and retrieves related notes from the server.
    # Get the topic from the user.
    topic = input("Enter the topic to retrieve notes for: ")
    # Request the notes from the server.
    response = send_request('GET', f"{server_url}/get_notes", params={'topic': topic})
    if response:
        notes = response.json()
        # If there are notes, print them.
        if notes:
            for note in notes:
                print(f"{note['name']}: {note['text']} (Timestamp: {note['timestamp']})")
        else:
            # If there are no notes for the topic, let the user know.
            print("No notes found for the given topic.")
    else:
        # If the request failed, let the user know.
        print("Failed to retrieve notes due to a request error.")


def delete_all_notes():  # Sends a request to the server to delete all notes.
    response = send_request('POST', f"{server_url}/delete_all_notes")
    if response:
        # If successful, print the server's response.
        print(response.json())
    else:
        # If the request failed, let the user know.
        print("Failed to delete all notes due to a request error.")


def search_notes():  # Searches for notes containing a specified keyword and prints them.
    keyword = input("Enter the keyword to search for in notes: ")
    response = send_request('GET', f"{server_url}/search_notes", params={'keyword': keyword})
    if response:
        notes = response.json()
        if notes:
            # If notes are found, print them.
            for note in notes:
                print(f"Topic: {note['topic']}, {note['name']}: {note['text']} (Timestamp: {note['timestamp']})")
        else:
            # If no notes contain the keyword, let the user know.
            print("No notes found containing the keyword.")
    else:
        # If the request failed, let the user know.
        print("Failed to search notes due to a request error.")


def add_wiki_info():  # Appends Wikipedia information related to a search term to a note under a specific topic.

    topic = input("Enter the topic to append Wikipedia info to: ")
    search_term = input("Enter the search term for Wikipedia: ")
    # Send the request to the server.
    response = send_request('POST', f"{server_url}/add_wiki_info", json={'topic': topic, 'search_term': search_term})
    if response:
        # If successful, print the server's response.
        print(response.json())
    else:
        # If the request failed, let the user know.
        print("Failed to add Wikipedia information due to a request error.")


def main():  # The main loop of the application, presenting options to the user and processing their choice.
    while True:
        print("\nOptions:\n1. Add a note\n2. Get notes by topic\n3. Delete all notes\n4. Search notes by keyword\n5. "
              "Add Wikipedia info to a topic\n6. Exit")
        choice = input("Enter your choice: ")
        # Process the user's choice by calling the corresponding function.
        if choice == '1':
            add_note()
        elif choice == '2':
            get_notes()
        elif choice == '3':
            delete_all_notes()
        elif choice == '4':
            search_notes()
        elif choice == '5':
            add_wiki_info()
        elif choice == '6':
            # Exit the application.
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()  # Start the application.
