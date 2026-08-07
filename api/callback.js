export default async function handler(req, res) {
  const { code } = req.query;
  const { OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET } = process.env;

  if (!code) {
    res.status(400).send('Missing code');
    return;
  }

  try {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ client_id: OAUTH_CLIENT_ID, client_secret: OAUTH_CLIENT_SECRET, code }),
    });

    const data = await response.json();
    const token = data.access_token;

    if (token) {
      const content = JSON.stringify({ token, provider: 'github' });
      const message = `authorization:github:success:${content}`;
      res.setHeader('Content-Type', 'text/html');
      res.send(`<!DOCTYPE html><html><body>
        <p>로그인 중...</p>
        <script>
          var msg = ${JSON.stringify(message)};
          try {
            if (window.opener) {
              window.opener.postMessage(msg, '*');
              setTimeout(function() { window.close(); }, 500);
            } else {
              document.body.innerHTML = '<p>창을 닫고 다시 시도해주세요.</p>';
            }
          } catch(e) {
            document.body.innerHTML = '<p>오류: ' + e.message + '</p>';
          }
        <\/script>
      </body></html>`);
    } else {
      res.setHeader('Content-Type', 'text/html');
      res.send(`<!DOCTYPE html><html><body><p>인증 실패: ${JSON.stringify(data)}</p></body></html>`);
    }
  } catch (e) {
    res.status(500).send('Server error: ' + e.message);
  }
}
