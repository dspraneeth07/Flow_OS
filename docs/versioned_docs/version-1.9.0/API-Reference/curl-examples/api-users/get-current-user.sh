curl -X GET \
  "$FLOWOS_URL/api/v1/users/whoami" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
