curl -X POST \
  "$FLOWOS_SERVER_URL/api/v2/workflows/stop" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -d '{
    "job_id": "job_id_1234567890"
  }'
