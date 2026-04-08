# 🕸️ Dev Environment Graph

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![PyPI Version](https://img.shields.io/pypi/v/dev-environment-graph) ![GitHub Stars](https://img.shields.io/github/stars/dev-tools/dev-environment-graph)

A powerful CLI tool that maps and visualizes local development services, ports, and interdependencies in real-time. Designed for developers and DevOps engineers managing complex local infrastructure, `dev-environment-graph` provides instant visibility into your running processes, network topology, and health status.

## ✨ Features

*   **Automatic Service Discovery**: Scans your local environment to detect active processes and services without manual configuration.
*   **Port Mapping**: Accurately maps running processes to their assigned network ports (TCP/UDP).
*   **Dependency Resolution**: Analyzes connection logs and configuration files to determine service interdependencies.
*   **Real-Time Health Monitoring**: Performs active health checks on identified services to detect failures immediately.
*   **Visual Topology**: Generates high-quality SVG or PNG graph representations of your environment architecture.
*   **CI/CD Integration**: Export environment maps to JSON for automated testing and deployment pipelines.
*   **Change Alerts**: Triggers notifications when service topology changes or critical dependencies break.

## 📦 Installation

`dev-environment-graph` requires Python 3.8+. You can install the package from PyPI:

```bash
pip install dev-environment-graph
```

**Note:** To render graph visualizations (SVG/PNG), ensure the Graphviz system library is installed on your OS:
*   **macOS**: `brew install graphviz`
*   **Linux (Ubuntu/Debian)**: `sudo apt-get install graphviz`
*   **Windows**: Download the installer from [graphviz.org](https://graphviz.org/download/) and add it to your PATH.

## 🚀 Quick Start

Once installed, you can scan your current environment and visualize it in seconds.

```bash
# Scan and generate a topology graph
dev-environment-graph scan --output topology.svg

# View the health status of all discovered services
dev-environment-graph health --all
```

## 🛠️ Usage

### Core Commands

| Command | Description |
| :--- | :--- |
| `dev-environment-graph` | Show the main help menu. |
| `dev-environment-graph scan` | Scan and build the environment map. |
| `dev-environment-graph render` | Generate visual graphs from the map. |
| `dev-environment-graph export` | Export data to JSON. |
| `dev-environment-graph monitor` | Start the alert system. |

### Examples

**Generate a graph based on connection logs:**

```bash
dev-environment-graph render \
  --input ./config/connections.json \
  --output ./visualizations/backend-topology.png \
  --format png
```

**Export environment data for CI/CD pipelines:**

```bash
dev-environment-graph export \
  --format json \
  --output ./reports/env-data.json \
  --exclude-debug-ports
```

**Start the monitoring daemon:**

```bash
dev-environment-graph monitor \
  --interval 30s \
  --notify-slack \
  --slack-webhook-url https://hooks.slack.com/services/...
```

## 🏗️ Architecture

The project is modular, allowing components to be reused or extended. It is built using the following tech stack: `python`, `click`, `networkx`, and `graphviz`.

*   **`service_discovery`**: Scans the local environment for active services and processes.
*   **`port_mapping`**: Maps running processes to their assigned network ports.
*   **`dependency_resolver`**: Analyzes service dependencies based on connection logs and config files.
*   **`health_monitor`**: Performs active health checks on identified services.
*   **`graph_renderer`**: Generates visual graph representations (SVG/PNG) of the environment topology.
*   **`export_engine`**: Exports the environment map to JSON for CI/CD integration.
*   **`alert_system`**: Triggers notifications when service topology changes or dependencies break.

## 🤝 Contributing

Contributions are welcome! Please follow these steps to get started:

1.  Fork the repository on GitHub.
2.  Clone your fork: `git clone https://github.com/your-username/dev-environment-graph.git`
3.  Create a feature branch: `git checkout -b feature/your-feature-name`
4