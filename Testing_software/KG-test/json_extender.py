import json


def validate_relationship_entry(entry):
    # Define the required keys and their expected subkeys and types
    required_keys = {
        'type': str,
        'from_node': {'type': str, 'text': str},
        'to_node': {'type': str, 'text': str}
    }

    if not all(key in entry for key in required_keys):
        return False

    if not isinstance(entry['type'], required_keys['type']):
        return False

    for node_key in ['from_node', 'to_node']:
        if not isinstance(entry[node_key], dict):
            return False
        for subkey, expected_type in required_keys[node_key].items():
            if subkey not in entry[node_key] or not isinstance(entry[node_key][subkey], expected_type):
                return False

    return True


def relationship_exists(existing_relationships, new_entry):
  # Use 'any' to check if a similar entry already exists
  return any(rel['type'] == new_entry['type'] and
             rel['from_node'] == new_entry['from_node'] and
             rel['to_node'] == new_entry['to_node']
             for rel in existing_relationships)


def extend_json_relationships(existing_json, new_json):
    # Check if both JSON objects have the 'relationships' key and it is a list
    if 'relationships' not in existing_json or 'relationships' not in new_json:
        raise ValueError("Both JSON objects must contain a 'relationships' key.")

    if not isinstance(existing_json['relationships'], list) or not isinstance(new_json['relationships'], list):
        raise ValueError("The 'relationships' key must be associated with a list.")

    # Validate each entry in the new relationships
    for entry in new_json['relationships']:
        if not validate_relationship_entry(entry):
            raise ValueError("All new entries must match the required format and data types.")

        if not relationship_exists(existing_json['relationships'], entry):
            existing_json['relationships'].append(entry)
