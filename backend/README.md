# MediaSaver Backend

This is the Python backend for the MediaSaver application. It uses **FastAPI** and **yt-dlp** to process video URLs.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup & Run

1. Open a terminal and navigate to this folder:
   ```bash
   cd backend
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: On some systems you might need to use `pip3`.*

3. Run the server:
   ```bash
   python main.py
   ```
   
   *Note: On some systems you might need to use `python3`.*

The server will start at `http://localhost:8000`. The frontend application is configured to communicate with this address.