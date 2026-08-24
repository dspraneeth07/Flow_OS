curl -X PUT \
  "$FLOWOS_URL/api/v2/files/$FILE_ID?name=new_file_name" \
  -H "accept: application/json" \
  -H "x-api-key: $FLOWOS_API_KEY"
