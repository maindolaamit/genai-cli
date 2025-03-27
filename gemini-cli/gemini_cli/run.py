"""
Main entry point for the Gemini CLI application.
This module provides the entry point that will be called by the gemini-cli command.
"""

def main():
    """Entry point for the gemini-cli command."""
    # Use a relative import to get the main function from cli.py
    from .cli import main as cli_main
    cli_main()


if __name__ == '__main__':
    main()