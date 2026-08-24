BASE_URL="${FLOWOS_SERVER_URL:-$FLOWOS_URL}"

curl -X POST \
  "$BASE_URL/api/v1/responses" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "model": "$FLOW_ID",
  "input": "Hello, my name is Alice"
}
EOF
