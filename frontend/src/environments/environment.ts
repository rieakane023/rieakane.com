// Local dev: API base is empty so requests stay relative (`/api/...`) and the
// `ng serve` proxy (proxy.conf.json) forwards them to the backend on :8000.
export const environment = {
  production: false,
  apiBaseUrl: '',
};
