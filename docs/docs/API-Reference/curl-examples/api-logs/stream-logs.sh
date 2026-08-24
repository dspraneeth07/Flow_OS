curl -X GET \
  "$FLOWOS_URL/logs-stream" \
  -H "accept: text/event-stream" \
  -H "x-api-key: $FLOWOS_API_KEY"
