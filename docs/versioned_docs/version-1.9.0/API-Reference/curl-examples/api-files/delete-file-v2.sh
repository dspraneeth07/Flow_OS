curl -X DELETE \
  "$FLOWOS_URL/api/v2/files/$FILE_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
