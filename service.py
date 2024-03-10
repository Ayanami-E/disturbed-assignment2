from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
import requests

app = Flask(__name__)
lock = threading.RLock()  # Re-entrant locking is a synchronization mechanism to prevent overlapping reads and writes


# and to protect the integrity of the database.


def load_or_create_xml():  # Loads a existed XML database file or creates a new XML database.
    try:
        tree = ET.parse('notes.xml')
        return tree, tree.getroot()
    except FileNotFoundError:
        new_tree = ET.ElementTree(ET.Element('data'))
        new_tree.write('notes.xml')  # Create file to avoid FileNotFoundError in subsequent operations
        return new_tree, new_tree.getroot()
    except ET.ParseError as e:
        # Log the parsing error here
        raise ET.ParseError(f"XML parsing error: {str(e)}")


def save_xml(tree):  # Save XML database file, use locks to secure threads Anchor
    with lock:
        try:
            tree.write('notes.xml')
        except Exception as e:  # Prevent errors from being thrown due to write permissions, lack of disk space, etc.
            raise Exception(f"Failed to save XML: {str(e)}")


@app.route('/')
def home():  # send welcome words
    return "Welcome to the Note Taking App!"


@app.route('/add_note', methods=['POST'])
def add_note():  # Adding annotations to subject-specific XML databases
    try:
        tree, root = load_or_create_xml()
    except Exception as e:  # Prevents errors such as file non-existence and XML parsing errors
        return jsonify({'error': str(e)}), 500

    data = request.json
    topic, name, text = data.get('topic'), data.get('name'), data.get('text')

    if not (topic and name and text):
        return jsonify({'error': 'Missing data for topic, name, or text'}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with lock:
        topic_element = root.find(f".//topic[@name='{topic}']")
        if not topic_element:
            topic_element = ET.SubElement(root, 'topic', name=topic)
        note_element = ET.SubElement(topic_element, 'note', name=name)
        ET.SubElement(note_element, 'text').text = text
        ET.SubElement(note_element, 'timestamp').text = timestamp

        try:
            save_xml(tree)
        except Exception as e:  # Prevention of file system problems
            return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Note added successfully'}), 200


@app.route('/get_notes', methods=['GET'])
def get_notes():
    topic = request.args.get('topic')  # find the special topic
    try:
        tree, root = load_or_create_xml()  # We find a XML or create a XML database
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # If any error occurs, return json error message

    topic_element = root.find(f".//topic[@name='{topic}']")
    if topic_element is None:
        return jsonify({'message': f'Topic "{topic}" not found'}), 404

    notes = []
    for note in topic_element.findall('note'):  # Append a dictionary containing the note's name, text, and timestamp
        # to the notes list
        notes.append({
            'name': note.get('name'),
            'text': note.find('text').text,
            'timestamp': note.find('timestamp').text
        })

    return jsonify(notes), 200


@app.route('/search_notes', methods=['GET'])
def search_notes():
    keyword = request.args.get('keyword')  # Get the query keywords from inside the query parameters
    try:  # This is same as get_notes
        tree, root = load_or_create_xml()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    found_notes = []  # Create a list to store notes that match keywords
    for topic_element in root.findall('.//topic'):  # Iterate through all the topics
        for note in topic_element.findall('note'):
            if keyword.lower() in note.find('text').text.lower():
                found_notes.append({  # If the process find the related note, the process append it to the list
                    'topic': topic_element.get('name'),
                    'name': note.get('name'),
                    'text': note.find('text').text,
                    'timestamp': note.find('timestamp').text
                })

    if not found_notes:  # Nothing for find
        return jsonify({'message': f'No notes found containing keyword "{keyword}"'}), 404

    return jsonify(found_notes), 200


@app.route('/add_wiki_info', methods=['POST'])
def add_wiki_info():
    data = request.json
    topic = data.get('topic')
    search_term = data.get('search_term')  # Read topics and keywords

    if not (topic and search_term):  # check topic and search term
        return jsonify({'error': 'Missing topic or search term'}), 400  # If not, return an error indicating missing
        # data

    try:
        tree, root = load_or_create_xml()  # try to find or load
    except Exception as e:  # if not, return the error
        return jsonify({'error': str(e)}), 500

    wiki_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_term}&limit=1&namespace=0&format=json"

    try:
        response = requests.get(wiki_url)  # Use the API to get the response
        response.raise_for_status()  # Raise an exception for HTTP errors
        wiki_data = response.json()  # Check if Wikipedia returned any results
        if wiki_data and len(wiki_data) > 1:
            wiki_info = wiki_data[3][0] if wiki_data[3] else "No URL found"  # Extract the URL of the first one
            note_name = f"Wikipedia Info: {search_term}"
            note_text = f"Wikipedia link: {wiki_info}"
            # Find or create the topic element in the XML
            topic_element = root.find(f".//topic[@name='{topic}']")
            if not topic_element:
                topic_element = ET.SubElement(root, 'topic', name=topic)
            note_element = ET.SubElement(topic_element, 'note', name=note_name)  # Add the new note under the topic
            ET.SubElement(note_element, 'text').text = note_text
            ET.SubElement(note_element, 'timestamp').text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_xml(tree)  # Save the updated XML to file
        else:  # Without the wiki article
            return jsonify({'message': 'No Wikipedia article found for the search term'}), 404
    except requests.RequestException as e:  # API error handling
        return jsonify({'error': 'Failed to query Wikipedia', 'message': str(e)}), 500
    except ValueError as e:  # Handling JSON encoding errors
        return jsonify({'error': 'Failed to decode Wikipedia response', 'message': str(e)}), 500
    except Exception as e:  # Handling other errors
        return jsonify({'error': 'Failed to add Wikipedia information', 'message': str(e)}), 500

    return jsonify({'message': 'Wikipedia information added successfully'}), 200  # return success message


@app.route('/delete_all_notes', methods=['POST'])
def delete_all_notes():
    # Try to load an existing XML file
    try:
        tree, root = load_or_create_xml()
        # Remove all <note> elements
        for topic in root.findall('topic'):
            for note in topic.findall('note'):
                topic.remove(note)

        # Save the changed XML file
        save_xml(tree)
        return jsonify({'message': 'All notes deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f"Failed to delete all notes: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=9090)
