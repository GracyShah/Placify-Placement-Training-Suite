import sys
sys.dont_write_bytecode = True

import os
import tempfile
from pathlib import Path

from flask import Flask

from db import init_app as init_db
from routes import routes_bp

runtime_root = (
    os.environ.get("PLACIFY_DATA_DIR")
    or os.environ.get("RENDER_DISK_PATH")
    or tempfile.gettempdir()
)
RUNTIME_DIR = Path(runtime_root) / "placify"

app = Flask(__name__, instance_relative_config=True)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "placify-secret-key-change-in-production"),
    DATABASE_PATH=os.environ.get("DATABASE_PATH", str(RUNTIME_DIR / "placify.db")),
    UPLOAD_FOLDER=os.environ.get("UPLOAD_FOLDER", str(RUNTIME_DIR / "uploads")),
    DOWNLOAD_FOLDER=os.environ.get("DOWNLOAD_FOLDER", str(RUNTIME_DIR / "downloads")),
    OPENAI_MODEL=os.environ.get("OPENAI_MODEL", "gpt-5.2"),
)

init_db(app)
app.register_blueprint(routes_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
