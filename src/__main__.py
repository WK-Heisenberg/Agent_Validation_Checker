# /a2a-validation-agent/src/__main__.py

import uvicorn
from .agent import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)