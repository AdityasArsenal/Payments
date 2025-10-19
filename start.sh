#!/bin/bash
# Startup script for PhonePe Payment App

echo "Starting PhonePe Payment App..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "menv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv menv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source menv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "⚠️  Warning: config.env not found!"
    echo "Using default credentials from code."
    echo "For production, copy config.env.example to config.env and update it."
fi

# Start the application
echo ""
echo "Starting Flask application..."
echo "Access the app at: http://localhost:5000"
echo "Press CTRL+C to stop"
echo ""
python f.py

