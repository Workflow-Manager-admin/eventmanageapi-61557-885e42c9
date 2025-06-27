#!/bin/bash
cd /home/kavia/workspace/code-generation/eventmanageapi-61557-885e42c9/event_management_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

