curl -v -X DELETE \
  "$FLOWOS_URL/api/v1/monitor/messages" \
  -H "accept: */*" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -d '["MESSAGE_ID_1", "MESSAGE_ID_2"]'
