# Contributing to Offline Wikipedia MCP Server

First off, thank you for considering contributing to this project! It's people like you that make open-source such a great community.

## 🐛 Reporting Bugs
If you find a bug, please check the existing issues first to see if it has already been reported. If not, open a new issue using the **Bug Report** template. Please include:
* Your operating system (Windows, Mac, Linux)
* Your MCP client (LM Studio, Claude Desktop, Cursor, etc.)
* The exact error message from the logs
* Which `.zim` file you are using

## ✨ Suggesting Enhancements
Want to add a new feature? Great! Open an issue using the **Feature Request** template. Describe the feature, why you need it, and how it should work.

## 🛠️ Pull Requests
If you want to write code and submit a Pull Request (PR):

1. **Fork the repository** to your own GitHub account.
2. **Clone your fork** locally.
3. **Create a branch** for your feature or bugfix (`git checkout -b feature/amazing-idea`).
4. **Make your changes** and test them locally using your MCP client.
5. **Commit your changes** with clear, descriptive commit messages.
6. **Push the branch** to your fork (`git push origin feature/amazing-idea`).
7. **Open a Pull Request** against the `main` branch of this repository.

### Development Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt