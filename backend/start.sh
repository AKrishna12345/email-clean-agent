#!/bin/bash
# Script to start the backend server

cd "$(dirname "$0")"
source venv/bin/activate
python3 -m uvicorn main:app --reload

