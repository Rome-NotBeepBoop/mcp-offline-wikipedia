# Offline Wikipedia MCP Server 📚🔌

A fast, completely offline Model Context Protocol (MCP) server that connects local LLMs to downloaded Kiwix Wikipedia archives (`.zim` files).

This project bridges the gap between locally hosted Large Language Models (like those running in LM Studio, Claude Desktop, or Ollama) and massive offline knowledge bases. By using the official Python MCP SDK and `libzim`, your LLM can search and read full Wikipedia articles without an internet connection.

## 📥 Required Downloads

To use this server, you need to download a Wikipedia `.zim` archive. Because LLMs only process text, it is highly recommended to download the **"mini"** or **"nopic"** (no pictures) versions of Wikipedia to save disk space.

1. **Go to the Kiwix Archive:** [https://library.kiwix.org/?lang=eng&q=wikipedia](https://library.kiwix.org/?lang=eng&q=wikipedia)
2. **Recommended Files to Download:**
   * **Wikipedia English (Mini):** Contains text, lists, and tables. No images. (~10GB - 15GB)
   * **Wikipedia English (Maxi):** Full Wikipedia with images. (~100GB+)
3. Download the `.zim` file to a permanent location on your hard drive (e.g., `D:\Datasets\wikipedia_en_all_mini.zim`).

## 🚀 Installation

Clone this repository and set up a Python virtual environment:

```bash
git clone [https://github.com/YOUR_USERNAME/mcp-offline-wikipedia.git](https://github.com/YOUR_USERNAME/mcp-offline-wikipedia.git)
cd mcp-offline-wikipedia

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt