#!/bin/sh

# Run the pre-start script
echo "Running the DB generating script..."
python devtools/generate_dataset.py

# Start the FastAPI server
echo "Starting FastAPI server..."
fastapi run src/application.py --port 80
