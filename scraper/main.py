# Python Imports
import logging
from io import StringIO
from contextlib import redirect_stdout

# Third-Party Imports
import webview

# Local imports
from server import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    stream = StringIO()
    with redirect_stdout(stream):
        window = webview.create_window("Joe's DFS", app)
        webview.start(window, debug=True)
