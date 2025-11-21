// API endpoint configuration for Amethyst

const ENV_MODE = process.env.NEXT_PUBLIC_ENV_MODE || 'dev';

export const amethystApiPath =
  process.env.NEXT_PUBLIC_AMETHYST_API_ENV === 'dev'
    ? 'http://localhost:8000'
    : 'https://amethyst.test.fask-svcs.faskai.com';

