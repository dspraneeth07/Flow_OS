curl -X GET \
  "$FLOWOS_URL/api/v1/flows/$FLOW_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
