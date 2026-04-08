import pytest
from unittest import mock
import graph_renderer
import io

# Fixture for sample topology data
@pytest.fixture
def sample_topology():
    return {
        "nodes": [
            {"id": "db", "label": "Database", "type": "server"},
            {"id": "api", "label": "API Server", "type": "server"}
        ],
        "edges": [
            {"source": "db", "target": "api", "relation": "connects_to"}
        ],
        "metadata": {"version": "1.0", "env": "dev"}
    }

# Fixture for invalid topology data
@pytest.fixture
def invalid_topology():
    return {
        "nodes": [],
        "edges": [{"source": "nonexistent", "target": "missing", "relation": "connects_to"}]
    }

# Fixture for mocking underlying graphics libraries
@pytest.fixture
def mock_graph_libraries():
    with mock.patch('graph_renderer.svgwrite') as mock_svgwrite, \
         mock.patch('graph_renderer.PIL') as mock_pil, \
         mock.patch('graph_renderer.io') as mock_io:
        
        mock_svg_instance = mock.MagicMock()
        mock_svgwrite.SVG.return_value = mock_svg_instance
        mock_svgwrite.Drawing.return_value = mock_svg_instance
        
        mock_png_instance = mock.MagicMock()
        mock_pil.Image.open.return_value = mock_png_instance
        
        mock_io.BytesIO.return_value = mock_bytes_io = mock.MagicMock()
        
        yield {
            'svgwrite': mock_svgwrite,
            'PIL': mock_pil,
            'io': mock_io
        }

class TestGraphRendererSVG:
    @mock.patch('graph_renderer.svgwrite')
    @mock.patch('graph_renderer.svgwrite.Drawing')
    def test_render_svg_success(self, mock_draw, mock_svg):
        instance = mock.MagicMock()
        mock_draw.return_value = instance
        mock_svg.SVG.return_value = instance
        
        result = graph_renderer.render_svg(sample_topology)
        
        mock_draw.assert_called_once()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_svg_empty_topology(self, mock_graph_libraries):
        with pytest.raises(ValueError) as exc_info:
            graph_renderer.render_svg({"nodes": [], "edges": []})
        assert "nodes" in str(exc_info.value).lower()

    @mock.patch('graph_renderer.svgwrite')
    def test_render_svg_missing_metadata(self, mock_svg):
        instance = mock.MagicMock()
        mock_svg.SVG.return_value = instance
        mock_svg.Drawing.return_value = instance
        
        topology = sample_topology.copy()
        topology.pop("metadata", None)
        
        result = graph_renderer.render_svg(topology)
        
        mock_svg.SVG.assert_called()
        assert isinstance(result, str)

class TestGraphRendererPNG:
    @mock.patch('graph_renderer.svgwrite')
    @mock.patch('graph_renderer.PIL')
    def test_render_png_save_to_file(self, mock_pil, mock_svg, mock_graph_libraries):
        mock_draw = mock.MagicMock()
        mock_svg.Drawing.return_value = mock_draw
        mock_img = mock.MagicMock()
        mock_pil.Image.new.return_value = mock_img
        
        mock_png_instance = mock.MagicMock()
        mock_pil.Image.open.return_value = mock_png_instance
        
        with mock.patch.object(mock_png_instance, 'save') as mock_save:
            graph_renderer.render_png(sample_topology, output_path="test_output.png")
            mock_save.assert_called()

    def test_render_png_return_bytes(self, mock_graph_libraries):
        mock_draw = mock.MagicMock()
        mock_graph_libraries['svgwrite'].Drawing.return_value = mock_draw
        mock_png_instance = mock.MagicMock()
        mock_graph_libraries['PIL'].Image.new.return_value = mock_png_instance
        
        mock_png_instance.save = mock.MagicMock(side_effect=lambda *args: mock_bytes_io.write(b"PNG_BYTES"))
        
        with mock.patch('graph_renderer.io.BytesIO', return_value=mock_bytes_io):
            result = graph_renderer.render_png(sample_topology)
            
        assert isinstance(result, bytes)

    @mock.patch('graph_renderer.svgwrite')
    def test_render_png_invalid_path(self, mock_svg):
        mock_draw = mock.MagicMock()
        mock_svg.Drawing.return_value = mock_draw
        mock_png_instance = mock.MagicMock()
        mock_graph_libraries['PIL'].Image.new.return_value = mock_png_instance
        
        with pytest.raises(OSError):
            graph_renderer.render_png(sample_topology, output_path="/nonexistent/directory/file.png")

class TestGraphRendererValidation:
    def test_validate_topology_valid(self, sample_topology):
        is_valid, message = graph_renderer.validate_topology(sample_topology)
        
        assert is_valid is True
        assert "error" not in message.lower()

    def test_validate_topology_invalid_structure(self, invalid_topology):
        is_valid, message = graph_renderer.validate_topology(invalid_topology)
        
        assert is_valid is False
        assert "error" in message.lower() or len(message) > 0

    def test_validate_topology_missing_required_keys(self):
        incomplete = {"nodes": [{"id": "1"}]}
        
        is_valid, message = graph_renderer.validate_topology(incomplete)
        
        assert is_valid is False
        assert "edges" in message.lower()

class TestGraphRendererErrorHandling:
    @mock.patch('graph_renderer.svgwrite')
    def test_render_svg_module_exception(self, mock_svg):
        mock_svg.SVG.side_effect = Exception("Lib failure")
        
        with pytest.raises(Exception):
            graph_renderer.render_svg(sample_topology)

    @mock.patch('graph_renderer.svgwrite')
    def test_render_svg_node_attribute_error(self, mock_svg):
        mock_draw = mock.MagicMock()
        mock_svg.Drawing.return_value = mock_draw
        mock_draw.addElement.side_effect = AttributeError("No element method")
        
        with pytest.raises(AttributeError):
            graph_renderer.render_svg(sample_topology)

    @mock.patch('graph_renderer.svgwrite')
    def test_render_svg_empty_nodes_list(self, mock_svg):
        mock_draw = mock.MagicMock()
        mock_svg.Drawing.return_value = mock_draw
        mock_svg.SVG.return_value = mock_draw
        
        topology = {"nodes": [], "edges": [], "metadata": {}}
        result = graph_renderer.render_svg(topology)
        
        assert result is not None

class TestGraphRendererFixtures:
    def test_sample_topology_has_nodes(self, sample_topology):
        assert isinstance(sample_topology.get("nodes"), list)
        assert len(sample_topology.get("nodes")) > 0

    def test_sample_topology_has_edges(self, sample_topology):
        assert isinstance(sample_topology.get("edges"), list)

    def test_invalid_topology_has_no_matching_refs(self, invalid_topology):
        invalid_edges = invalid_topology.get("edges", [])
        if invalid_edges:
            assert invalid_edges[0].get("source") not in [n["id"] for n in invalid_topology.get("nodes", [])]