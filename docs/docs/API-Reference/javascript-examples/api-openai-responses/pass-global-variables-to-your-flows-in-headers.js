const url = `${process.env.FLOWOS_SERVER_URL ?? ""}/api/v1/responses`;

const options = {
  method: 'POST',
  headers: {
    "x-api-key": `${process.env.FLOWOS_API_KEY ?? ""}`,
    "Content-Type": `application/json`,
    "X-FLOWOS-GLOBAL-VAR-OPENAI_API_KEY": `sk-...`,
    "X-FLOWOS-GLOBAL-VAR-USER_ID": `user123`,
    "X-FLOWOS-GLOBAL-VAR-ENVIRONMENT": `production`,
  },
  body: JSON.stringify({
  "model": "your-flow-id",
  "input": "Hello"
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
