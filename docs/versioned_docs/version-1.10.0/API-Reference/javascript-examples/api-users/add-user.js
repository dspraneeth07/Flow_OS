const url = `${process.env.FLOWOS_URL ?? ""}/api/v1/users/`;

const options = {
  method: 'POST',
  headers: {
    "Content-Type": `application/json`,
    "x-api-key": `${process.env.FLOWOS_API_KEY ?? ""}`,
  },
  body: JSON.stringify({
  "username": "newuser2",
  "password": "securepassword123"
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
