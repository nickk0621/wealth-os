"""Streamlit entry point for Wealth OS.

This wrapper imports the dashboard as a package module so its relative imports
resolve correctly when Streamlit executes the top-level script.
"""

from wealth_os.dashboard import *  # noqa: F401,F403
