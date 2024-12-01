import json
from server import shared_state

def save_data():
    data = {
        "users": shared_state.users,
        "relationships": shared_state.relationships,
        "messages": shared_state.messages
    }
    with open('server/data.json', 'w') as f:
        json.dump(data, f)
    print("data saved bro")

def load_data():
    try:
        with open('server/data.json', 'r') as f:
            data = json.load(f)
            shared_state.users.update(data["users"])
            shared_state.relationships.update(data["relationships"])
            shared_state.messages.extend(data["messages"])
    except FileNotFoundError:
        pass