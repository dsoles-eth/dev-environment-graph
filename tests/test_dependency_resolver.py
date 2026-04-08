import pytest
import sys
from unittest.mock import patch, mock_open, MagicMock
import json

# Ensure module can be imported from project root
sys.path.insert(0, '.')
import dependency_resolver


# --- Fixtures ---

@pytest.fixture
def valid_json_config():
    return {"service_name": "api-gateway", "dependencies": ["auth-service", "db-service"]}


@pytest.fixture
def log_content_with_connections():
    return """
2023-01-01 10:00:00 INFO Connection: api -> auth
2023-01-01 10:00:01 INFO Connection: auth -> db
2023-01-01 10:00:02 INFO Connection: api -> db
"""


@pytest.fixture
def empty_log_content():
    return ""


@pytest.fixture
def malformed_log_content():
    return """
2023-01-01 INFO Connection: api
2023-01-01 INFO Connection: missing_service
"""


@pytest.fixture
def dependency_graph():
    return {
        "api": ["auth", "db"],
        "auth": ["db"],
        "db": []
    }


@pytest.fixture
def cyclic_dependency_graph():
    return {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    }


@pytest.fixture
def sample_service():
    return "api"


# --- Tests for load_config ---

@patch("dependency_resolver.json.load")
@patch("builtins.open")
def test_load_config_success(mock_open, mock_json_load, valid_json_config):
    mock_file = mock_open()
    mock_file.return_value.read.return_value = json.dumps(valid_json_config)
    mock_json_load.return_value = valid_json_config
    
    result = dependency_resolver.load_config("config.json")
    
    assert isinstance(result, dict)
    assert "service_name" in result
    assert result["service_name"] == "api-gateway"
    mock_open.assert_called_once_with("config.json")


@patch("builtins.open", side_effect=FileNotFoundError)
def test_load_config_file_not_found(mock_open):
    with pytest.raises(FileNotFoundError):
        dependency_resolver.load_config("non_existent.json")
    mock_open.assert_called_once_with("non_existent.json")


@patch("builtins.open")
@patch("dependency_resolver.json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
def test_load_config_invalid_json(mock_json_load, mock_open):
    mock_file = mock_open()
    mock_file.return_value.read.return_value = "{ invalid json"
    
    with pytest.raises(json.JSONDecodeError):
        dependency_resolver.load_config("bad_config.json")
    
    mock_open.assert_called_once_with("bad_config.json")
    mock_json_load.assert_called_once()


# --- Tests for parse_connection_logs ---

def test_parse_logs_success(log_content_with_connections):
    result = dependency_resolver.parse_connection_logs(log_content_with_connections)
    
    assert len(result) >= 3
    assert ("api", "auth") in result
    assert ("auth", "db") in result
    assert ("api", "db") in result


def test_parse_logs_empty(empty_log_content):
    result = dependency_resolver.parse_connection_logs(empty_log_content)
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_parse_logs_malformed(malformed_log_content):
    with pytest.warns(UserWarning, match="Skipping malformed line"):
        result = dependency_resolver.parse_connection_logs(malformed_log_content)
    
    assert isinstance(result, list)
    # Malformed lines should be skipped, valid or invalid logic depends on implementation
    # Assuming empty result or filtered result for malformed data
    assert isinstance(result, list)


# --- Tests for build_dependency_graph ---

def test_build_graph_success(dependency_graph):
    result = dependency_resolver.build_dependency_graph(dependency_graph)
    
    assert result == dependency_graph
    assert isinstance(result, dict)
    assert "api" in result


def test_build_graph_empty():
    result = dependency_resolver.build_dependency_graph([])
    
    assert isinstance(result, dict)
    assert len(result) == 0


def test_build_graph_invalid_data():
    with pytest.raises(TypeError):
        dependency_resolver.build_dependency_graph("not_a_list")


# --- Tests for resolve_dependencies ---

@patch.object(dependency_resolver, 'parse_connection_logs')
def test_resolve_dependencies_happy_path(mock_parse_logs, dependency_graph):
    # Mock the internal graph retrieval or assume graph is passed
    result = dependency_resolver.resolve_dependencies("auth", dependency_graph)
    
    assert "db" in result