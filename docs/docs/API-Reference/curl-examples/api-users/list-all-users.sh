curl -X GET \
  "$FLOWOS_URL/api/v1/users/?skip=0&limit=10" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
