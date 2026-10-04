import json
import pytest

class LocalStorageMock:
    def __init__(self):
        self.store = {}

    def getItem(self, key):
        return self.store.get(key, None)

    def setItem(self, key, value):
        self.store[key] = str(value)

    def removeItem(self, key):
        if key in self.store:
            del self.store[key]

    def clear(self):
        self.store = {}

@pytest.fixture
def storage():
    return LocalStorageMock()

def test_note_crud_operations(storage):
    notes_key = "notes"
    initial_notes = [
        {
            "id": "1",
            "title": "Test Note",
            "content": "# Hello World",
            "tags": ["work"],
            "createdAt": 1600000000000,
            "updatedAt": 1600000000000
        }
    ]
    storage.setItem(notes_key, json.dumps(initial_notes))
    
    # Read
    data = json.loads(storage.getItem(notes_key))
    assert len(data) == 1
    assert data[0]["title"] == "Test Note"

    # Update
    data[0]["content"] = "# Updated Content"
    storage.setItem(notes_key, json.dumps(data))
    updated_data = json.loads(storage.getItem(notes_key))
    assert updated_data[0]["content"] == "# Updated Content"

    # Delete
    storage.setItem(notes_key, json.dumps([]))
    empty_data = json.loads(storage.getItem(notes_key))
    assert len(empty_data) == 0
