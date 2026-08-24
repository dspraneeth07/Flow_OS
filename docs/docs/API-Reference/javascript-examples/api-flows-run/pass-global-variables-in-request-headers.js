const url = `${process.env.FLOWOS_SERVER_URL ?? ""}/api/v1/run/${process.env.FLOW_ID ?? ""}`;

const options = {
  method: 'POST',
  headers: {
    "Content-Type": `application/json`,
    "x-api-key": `${process.env.FLOWOS_API_KEY ?? ""}`,
    "X-FLOWOS-GLOBAL-VAR-OPENAI_API_KEY": `sk-...`,
    "X-FLOWOS-GLOBAL-VAR-USER_ID": `user123`,
    "X-FLOWOS-GLOBAL-VAR-ENVIRONMENT": `production`,
  },
  body: JSON.stringify({
  "input_value": "Tell me about something interesting!",
  "input_type": "chat",
  "output_type": "chat"
}),
};

fetch(url, options)
  .then(async (response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const text = await response.text();
    console.log(text);
  })
  .catch((error) => console.error(error));
