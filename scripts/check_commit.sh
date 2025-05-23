#!/bin/bash

COMMIT_MSG_FILE=$1
REGEX="^(feat|fix|docs|style|refactor|test|chore): .+"

if ! grep -qE "$REGEX" "$COMMIT_MSG_FILE"; then
  echo "❌ Commit inválido!"
  echo "Use o formato: 'tipo: descrição'"
  echo "Ex: 'feat: adiciona rota de login'"
  exit 1
fi
