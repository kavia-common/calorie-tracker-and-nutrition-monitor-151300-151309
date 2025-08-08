#!/bin/bash
cd /home/kavia/workspace/code-generation/calorie-tracker-and-nutrition-monitor-151300-151309/calorie_tracker_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

