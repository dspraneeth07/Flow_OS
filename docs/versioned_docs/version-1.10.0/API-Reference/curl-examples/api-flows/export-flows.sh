curl -X POST \
  "$FLOWOS_URL/api/v1/flows/download/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY" \
  -d '[
  "e1e40c77-0541-41a9-88ab-ddb3419398b5",
  "92f9a4c5-cfc8-4656-ae63-1f0881163c28"
]' \
  --output flowos-flows.zip
