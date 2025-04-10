# Placement Allocation System

This is a Cargo Stowage Management System developed for the National Space Hackathon 2025. It automates container assignment based on item IDs, with features like search, retrieval, waste management, and time simulation.

## Features
- Placement recommendations
- Item search and retrieval
- Waste identification and removal
- Day simulation
- Import/export functionality
- Logging

## Requirements
- Python 3.x
- pandas
- flask
- containers.csv
- input_items.csv

## How to Run
1. **Locally**:
   - Install dependencies: `pip install pandas flask`
   - Place `containers.csv` and `input_items.csv` in the folder.
   - Run: `python app.py`
   - Access at `http://127.0.0.1:5000/`
2. **With Docker**:
   - Build the Docker image: `docker build -t hackathon_placement_system .`
   - Run the container: `docker run -p 8000:8000 hackathon_placement_system`
   - Access at `http://127.0.0.1:8000/`

## API Endpoints
- `/api/placement` (POST): Place an item
- `/api/search` (GET): Search items
- `/api/retrieve` (POST): Retrieve an item
- `/api/waste/identify` (GET): Identify waste
- `/api/waste/return-plan` (GET): Plan for waste return
- `/api/waste/complete-undocking` (POST): Complete waste undocking
- `/api/import/items` (POST): Import items
- `/api/import/containers` (POST): Import containers
- `/api/export/arrangement` (GET): Export arrangement
- `/api/simulate/day` (POST): Simulate a day
- `/api/logs` (GET): View logs

## Notes
- Ensure CSV files are present.
- Docker uses port 8000.
- All code is original and developed during the hackathon.
