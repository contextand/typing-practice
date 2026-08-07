export default async function handler(req, res) {
  const { code } = req.query;
  const { OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET } = process.env;

  const response = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ client_id: OAUTH_CLIENT_ID, client_secret: OAUTH_CLIENT_SECRET, code }),
  });

  const data = await response.json();

  if (data.access_token) {
    const script = `
<script>
  const msg = JSON.stringify({ token: "${data.access_token}", provider: "github" });
  window.opener.postMessage("authorization:github:success:" + msg, "*");
  window.close();
</script>`;
    res.setHeader('Content-Type', 'text/html');
    res.send(script);
  } else {
    res.status(400).send('OAuth failed');
  }
}
