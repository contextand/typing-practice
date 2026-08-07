export default async function handler(req, res) {
  const { code } = req.query;
  const { OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET } = process.env;

  try {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ client_id: OAUTH_CLIENT_ID, client_secret: OAUTH_CLIENT_SECRET, code }),
    });

    const data = await response.json();

    if (data.access_token) {
      const token = data.access_token;
      const content = JSON.stringify({ token, provider: 'github' });
      const message = `authorization:github:success:${content}`;
      res.setHeader('Content-Type', 'text/html');
      res.send(`<!DOCTYPE html><html><body><script>
        (function() {
          var msg = ${JSON.stringify(message)};
          if (window.opener) {
            window.opener.postMessage(msg, '*');
          }
          window.close();
        })();
      <\/script></body></html>`);
    } else {
      res.setHeader('Content-Type', 'text/html');
      res.send(`<!DOCTYPE html><html><body><script>
        (function() {
          var msg = 'authorization:github:error:' + JSON.stringify(${JSON.stringify(JSON.stringify(data))});
          if (window.opener) { window.opener.postMessage(msg, '*'); }
          window.close();
        })();
      <\/script></body></html>`);
    }
  } catch (e) {
    res.status(500).send('Server error: ' + e.message);
  }
}
