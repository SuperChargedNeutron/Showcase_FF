import logging
import webview

from contextlib import redirect_stdout
from io import StringIO
from server import app

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    stream = StringIO()
    with redirect_stdout(stream):
        window = webview.create_window("Joe's DFS", app)
        webview.start(debug=True)