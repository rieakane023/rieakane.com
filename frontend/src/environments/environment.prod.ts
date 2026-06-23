// Production build (Cloudflare Pages): call the Render backend by absolute URL,
// since Pages has no backend to proxy `/api` to. Not a secret — a public API URL.
export const environment = {
  production: true,
  apiBaseUrl: 'https://rieakane-backend-dev.onrender.com',
};
