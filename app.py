"""Streamlit entry point for Wealth OS.

Streamlit reruns this file on every interaction. We therefore execute the
wealth_os.dashboard module afresh on each rerun rather than importing it once,
which would be cached by Python and leave subsequent reruns blank.
"""

import runpy

runpy.run_module("wealth_os.dashboard", run_name="__main__")
