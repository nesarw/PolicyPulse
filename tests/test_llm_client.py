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
        assert result[0] == "Hello, this is a stubbed response."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale
        assert mock_post.call_count == 1  # Called once for reply only

def test_chat_handles_dict_response(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = {"generated_text": "Dict format response."}
    
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert result[0] == "Dict format response."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale

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
        assert result[0] == "Last format response."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale

def test_chat_model_not_found(llm_client):
    stubbed_response = Mock()
    stubbed_response.status_code = 404
    stubbed_response.json.return_value = {"error": "Model not found"}
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert "Model not found" in result[0]  # Check reply
        assert result[1] is None  # No rationale for error cases

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
        assert "unexpected" in result[0]  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale

def test_chat_with_kb_passages(llm_client):
    """Test chat method with knowledge base passages"""
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [{"generated_text": "Response with KB context."}]
    
    # Mock rationale response
    rationale_response = Mock()
    rationale_response.status_code = 200
    rationale_response.json.return_value = [{"generated_text": "Based on the KB passages provided."}]
    
    kb_passages = ["Health insurance covers medical expenses.", "Your policy number is 1234567890."]
    
    with patch("requests.post", side_effect=[stubbed_response, rationale_response]):
        result = llm_client.chat("What is my policy number?", kb_passages=kb_passages)
        assert result[0] == "Response with KB context."  # Check reply
        assert result[1] == "Based on the KB passages provided."   # Check rationale

def test_chat_without_kb_passages(llm_client):
    """Test chat method without knowledge base passages"""
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [{"generated_text": "Response without KB context."}]
    
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!")
        assert result[0] == "Response without KB context."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale

def test_chat_with_empty_kb_passages(llm_client):
    """Test chat method with empty knowledge base passages"""
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [{"generated_text": "Response with empty KB."}]
    
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!", kb_passages=[])
        assert result[0] == "Response with empty KB."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale

def test_chat_with_none_kb_passages(llm_client):
    """Test chat method with None knowledge base passages"""
    stubbed_response = Mock()
    stubbed_response.status_code = 200
    stubbed_response.json.return_value = [{"generated_text": "Response with None KB."}]
    
    with patch("requests.post", return_value=stubbed_response):
        result = llm_client.chat("Hi!", kb_passages=None)
        assert result[0] == "Response with None KB."  # Check reply
        assert result[1] == "No relevant facts or KB snippets were found for this answer."  # Check rationale
