import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, Mock
from utils.llm_client import LLMClient

@pytest.fixture
def llm_client():
    return LLMClient(api_key="test-key")

def test_chat_returns_stubbed_message(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [{"generated_text": "Hello, this is a stubbed response."}]
    with patch("requests.post", return_value=stubbed_response) as mock_post:
        result = llm_client.chat("Hi!")
        assert result == "Hello, this is a stubbed response."
        mock_post.assert_called_once()
