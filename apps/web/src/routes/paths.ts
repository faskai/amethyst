export const paths = {
  home: '/',
  about: '/about',
  apps: {
    root: '/apps',
    create: '/apps/create',
    details: (id: string) => `/apps/${id}`,
  },
  resources: {
    root: '/resources',
  },
};

