import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, Mock
from utils.llm_client import LLMClient
import requests

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

def test_chat_handles_dict_response(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = {"generated_text": "Dict format response."}
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert result == "Dict format response."

def test_chat_handles_list_last_element(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [
        {"generated_text": "First"},
        {"generated_text": "Second"},
        {"generated_text": "Last format response."}
    ]
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert result == "Last format response."

def test_chat_model_not_found(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 404
    stubbed_response.json.return_value = {"error": "Model not found"}
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert "Model not found" in result

def test_chat_raises_for_other_http_errors(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 500
    stubbed_response.raise_for_status.side_effect = requests.HTTPError("Server error")
    with patch("requests.post", return_value=stubbed_response):
        with pytest.raises(requests.HTTPError):
            llm_client.chat("Hi!")

def test_chat_handles_unexpected_response(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = {"unexpected": "format"}
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert "unexpected" in result
