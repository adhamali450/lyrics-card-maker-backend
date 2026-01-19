import os
from src.app import app

if __name__ == "__main__":
    is_dev = os.getenv("ENV") == "dev"
    app.run(host="0.0.0.0", port=5000, debug=is_dev)
