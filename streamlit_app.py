"""Streamlit Community Cloud entrypoint.

Keep the main application in app.py for local use while allowing deployments
that expect streamlit_app.py to run the same code.
"""

import app  # noqa: F401
