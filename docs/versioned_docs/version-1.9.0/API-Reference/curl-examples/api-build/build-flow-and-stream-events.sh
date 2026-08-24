curl -X POST \
  "$FLOWOS_URL/api/v1/build/$FLOW_ID/flow" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -d '{
    "inputs": {
      "input_value": "Tell me a story"
    }
  }'
