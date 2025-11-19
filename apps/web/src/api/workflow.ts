import axios from 'axios';

import { wfApiPath } from './api-constants';

export async function searchApps(query: string): Promise<any> {
  const res = await axios.get(`${wfApiPath}/connections/apps?q=${encodeURIComponent(query)}`);
  return res.data;
}

