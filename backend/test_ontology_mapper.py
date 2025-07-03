from unittest.mock import patch
from ontology_mapper import map_api_to_ontology

MOCK_MAPPING = {
    "endpoint_to_table": [
        {"endpoint": "/api/users", "table": "users"},
        {"endpoint": "/api/orders", "table": "orders"}
    ]
}

def mock_claude_call(*args, **kwargs):
    # Simulate Claude returning the correct mapping as JSON string
    class MockResponse:
        def __init__(self):
            self.content = [type('obj', (object,), {'text': str(MOCK_MAPPING).replace("'", '"')})()]
    return MockResponse()

@patch('ontology_mapper.claude_client')
def test_map_api_to_ontology(mock_client):
    mock_client.messages.create.side_effect = mock_claude_call
    api_spec = {"endpoints": [
        {"path": "/api/users", "data_type": "users"},
        {"path": "/api/orders", "data_type": "orders"}
    ], "data_models": []}
    ontology_schema = {"tables": [
        {"name": "users"},
        {"name": "orders"}
    ]}
    result = map_api_to_ontology(api_spec, ontology_schema)
    assert result == MOCK_MAPPING 