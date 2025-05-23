#!/bin/bash

COMMIT_MSG_FILE=$1
REGEX="^(feat|fix|docs|style|refactor|test|chore): .+"

if ! grep -qE "$REGEX" "$COMMIT_MSG_FILE"; then
  echo "❌ Invalid commit message format."
  echo "Please use the format: 'type: description'"
  echo "Example: 'feat: add login route'"
  exit 1
fi
