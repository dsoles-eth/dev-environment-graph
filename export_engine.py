import json
import click
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from graphviz import Digraph

class DevEnvironmentGraph(nx.DiGraph):
    """
    A graph representation of the local development environment using NetworkX.

    This class encapsulates services, ports, and their interdependencies,
    providing methods for manipulation and export.
    """

    def __init__(self, name: str = "DevEnvironment"):
        """
        Initialize the development environment graph.

        :param name: The name identifier for the development environment.
        """