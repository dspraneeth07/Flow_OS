curl -X POST \
  "$FLOWOS_SERVER_URL/api/v1/responses" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-FLOWOS-GLOBAL-VAR-OPENAI_API_KEY: sk-..." \
  -H "X-FLOWOS-GLOBAL-VAR-USER_ID: user123" \
  -H "X-FLOWOS-GLOBAL-VAR-ENVIRONMENT: production" \
  -d '{
    "model": "your-flow-id",
    "input": "Hello"
  }'
