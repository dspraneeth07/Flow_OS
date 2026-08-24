curl -X GET \
  "$FLOWOS_URL/api/v1/projects/$PROJECT_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
