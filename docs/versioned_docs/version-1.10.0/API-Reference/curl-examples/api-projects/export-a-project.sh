curl -X GET \
  "$FLOWOS_URL/api/v1/projects/download/$PROJECT_ID" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  --output flowos-project.zip
