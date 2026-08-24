curl -X POST \
  "$FLOWOS_SERVER_URL/api/v1/responses" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "FLOW_ID",
    "input": "Explain quantum computing in simple terms",
    "stream": false
  }'
