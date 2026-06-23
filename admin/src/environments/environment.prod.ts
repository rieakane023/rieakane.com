// Production deploy (prod environment): call the prod backend by absolute URL.
// Not a secret — a public API URL.
export const environment = {
  production: true,
  apiBaseUrl: 'https://api.rieakane.com',
};
