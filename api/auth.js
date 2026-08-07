export default function handler(req, res) {
  const { OAUTH_CLIENT_ID } = process.env;
  const scope = 'repo,user';
  const authUrl = `https://github.com/login/oauth/authorize?client_id=${OAUTH_CLIENT_ID}&scope=${scope}`;
  res.redirect(authUrl);
}
