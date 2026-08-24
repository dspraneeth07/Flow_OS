curl -X DELETE \
  "$FLOWOS_URL/api/v1/monitor/builds?flow_id=$FLOW_ID" \
  -H "accept: */*" \
  -H "x-api-key: $FLOWOS_API_KEY"
