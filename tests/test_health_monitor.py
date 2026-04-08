import pytest
from unittest.mock import patch, MagicMock, call
import health_monitor


@pytest.fixture
def sample_services():
    return [
        {"id": 1, "name": "api-gateway", "endpoint": "http://api.internal/health"},
        {"id": 2, "name": "database", "endpoint": "tcp://db.internal:5432"},
        {"id": 3, "name": "cache", "endpoint": "redis://cache.internal:6379"}
    ]


@pytest.fixture
def mock_http_response():
    response = MagicMock()
    response.status_code = 200
    response.text = '{"status": "ok"}'
    return response


@pytest.fixture
def mock_connection_error():
    import requests
    return requests.exceptions.ConnectionError("Connection refused")


@pytest.fixture
def mock_timeout_error():
    import requests
    return requests.exceptions.Timeout("Connection timed out")


class TestHealthMonitorServiceCheck:
    """Test cases for the check_service function."""

    @patch('health_monitor.requests.get')
    def test_check_service_happy_path(self, mock_get, sample_services):
        service = sample_services[0]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = health_monitor.check_service(service, timeout=5)

        assert result['status'] == 'healthy'
        assert result['service_id'] == 1
        assert result['latency_ms'] >= 0
        mock_get.assert_called_once_with(service['endpoint'], timeout=5)

    @patch('health_monitor.requests.get')
    def test_check_service_unhealthy_status(self, mock_get, sample_services):
        service = sample_services[0]
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        result = health_monitor.check_service(service, timeout=5)

        assert result['status'] == 'unhealthy'
        assert result['status_code'] == 503
        mock_get.assert_called_once()

    @patch('health_monitor.requests.get')
    def test_check_service_network_error(self, mock_get, sample_services):
        service = sample_services[0]
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        result = health_monitor.check_service(service, timeout=5)

        assert result['status'] == 'error'
        assert result['error_type'] == 'timeout'
        mock_get.assert_called_once()


class TestHealthMonitorBatchRun:
    """Test cases for the run_checks function."""

    @patch('health_monitor.check_service')
    def test_run_checks_all_success(self, mock_check, sample_services):
        mock_check.return_value = {"status": "healthy", "latency_ms": 120}
        results = health_monitor.run_checks(sample_services, timeout=5)

        assert len(results) == 3
        for res in results:
            assert res['status'] == 'healthy'
        assert mock_check.call_count == 3
        assert all(call[1].get('timeout') == 5 for call in mock_check.call_args_list)

    @patch('health_monitor.check_service')
    def test_run_checks_partial_failure(self, mock_check, sample_services):
        mock_check.side_effect = [
            {"status": "healthy", "latency_ms": 100},
            {"status": "unhealthy", "latency_ms": 500},
            {"status": "error", "error_type": "timeout"}
        ]
        results = health_monitor.run_checks(sample_services, timeout=5)

        statuses = [r['status'] for r in results]
        assert 'healthy' in statuses
        assert 'unhealthy' in statuses
        assert 'error' in statuses
        assert all(isinstance(r['service_id'], int) for r in results)

    @patch('health_monitor.check_service')
    def test_run_checks_empty_list(self, mock_check, sample_services):
        empty_services = []
        results = health_monitor.run_checks(empty_services, timeout=5)

        assert results == []
        mock_check.assert_not_called()


class TestHealthMonitorReportGeneration:
    """Test cases for the generate_report function."""

    def test_generate_report_full_data(self):
        mock_data = [
            {"service_id": 1, "status": "healthy", "latency_ms": 50},
            {"service_id": 2, "status": "healthy", "latency_ms": 60}
        ]
        report = health_monitor.generate_report(mock_data, format_type='json')

        assert report is not None
        assert len(report) > 0
        assert 'summary' in report

    def test_generate_report_empty_data(self):
        mock_data = []
        report = health_monitor.generate_report(mock_data, format_type='text')

        assert report is not None
        assert 'total_services' in report
        assert report['total_services'] == 0
        assert report['healthy_services'] == 0

    def test_generate_report_custom_formatting(self):
        mock_data = [
            {"service_id": 1, "status": "healthy", "latency_ms": 50}
        ]
        report_json = health_monitor.generate_report(mock_data, format_type='json')
        report_text = health_monitor.generate_report(mock_data, format_type='text')

        assert report_json is not None
        assert report_text is not None
        assert isinstance(report_text, str)
        assert 'healthy' in report_text.lower()