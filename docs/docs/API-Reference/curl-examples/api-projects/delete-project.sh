curl -X DELETE \
  "$FLOWOS_URL/api/v1/projects/$PROJECT_ID" \
  -H "accept: */*" \
  -H "x-api-key: $FLOWOS_API_KEY"
