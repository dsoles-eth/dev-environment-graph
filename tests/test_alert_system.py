import pytest
from unittest.mock import patch, MagicMock
import sys
import importlib

# Ensure the module can be imported
sys.path.insert(0, '.')
import alert_system

@pytest.fixture
def mock_graph():
    """Fixture providing a sample service topology graph."""
    return {
        "service_a": ["service_b", "service_c"],
        "service_b": ["service_d"],
        "service_c": [],
        "service_d": []
    }

@pytest.fixture
def mock_service_id():
    """Fixture providing a sample service identifier."""
    return "service-a-01"

@pytest.fixture
def mock_alert_client():
    """Fixture to mock the notification client."""
    with patch.object(alert_system, 'send_notification_external') as mock_client:
        mock_client.return_value = True
        yield mock_client

@pytest.fixture
def mock_previous_state():
    """Fixture for previous topology state."""
    return {
        "service_a": ["service_b"],
        "service_b": ["service_d"]
    }

@pytest.fixture
def mock_current_state():
    """Fixture for current topology state."""
    return {
        "service_a": ["service_b", "service_c"],
        "service_b": ["service_d"]
    }

class TestCheckDependencies:
    
    @patch('alert_system.alert_system')
    def test_check_dependencies_happy_path(self, mock_internal):
        """Test case 1: Verify correct detection of healthy dependencies."""
        graph = {
            "svc_1": ["svc_2"],
            "svc_2": []
        }
        result = alert_system.check_dependencies(graph)
        assert result == []
    
    @patch('alert_system.alert_system')
    def test_check_dependencies_broken_link(self, mock_internal):
        """Test case 2: Detect broken dependency in topology."""
        graph = {
            "svc_1": ["svc_nonexistent"],
            "svc_nonexistent": []
        }
        with patch('alert_system.check_node_exists', return_value=False):
            result = alert_system.check_dependencies(graph)
            assert "svc_1 -> svc_nonexistent" in result
            
    @patch('alert_system.alert_system')
    def test_check_dependencies_empty_graph(self, mock_internal):
        """Test case 3: Handle empty or null graph gracefully."""
        result = alert_system.check_dependencies({})
        assert result == []

class TestDetectTopologyChanges:
    
    def test_detect_topology_addition(self, mock_previous_state, mock_current_state):
        """Test case 1: Detect new service added to topology."""
        changes = alert_system.detect_topology_changes(mock_previous_state, mock_current_state)
        assert "service_c" in str(changes)
    
    def test_detect_topology_removal(self):
        """Test case 2: Detect service removed from topology."""
        previous = {
            "svc_a": ["svc_b"],
            "svc_b": []
        }
        current = {
            "svc_a": ["svc_b"]
            # svc_b removed
        }
        with patch.object(alert_system, 'check_dependencies'):
            changes = alert_system.detect_topology_changes(previous