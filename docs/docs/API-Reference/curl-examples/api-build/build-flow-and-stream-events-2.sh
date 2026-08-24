curl -X GET \
  "$FLOWOS_URL/api/v1/build/123e4567-e89b-12d3-a456-426614174000/events" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
