#!/bin/bash
# setup.sh - Setup Python venv, install requirements, and run main.py for this project

set -e

# 1. Create venv if it doesn't exist
if [ ! -d "damn-env" ]; then
    python3 -m venv damn-env
fi

# 2. Activate venv
source damn-env/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install requirements
pip install -r requirements.txt

# 5. Run main.py
python main.py
