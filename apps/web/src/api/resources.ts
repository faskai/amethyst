import axios from 'axios';

import { amethystApiPath } from './api-constants';

export interface Resource {
  name: string;
  provider: string;
  type: string;
  id?: string;
  img_url?: string;
}

export async function listResources() {
  const response = await axios.get(`${amethystApiPath}/resources/`);
  return response.data;
}

export async function createResource(resource: Resource) {
  const response = await axios.post(`${amethystApiPath}/resources/`, resource);
  return response.data;
}

export async function getResource(id: string) {
  const response = await axios.get(`${amethystApiPath}/resources/${id}`);
  return response.data;
}

export async function deleteResource(id: string) {
  const response = await axios.delete(`${amethystApiPath}/resources/${id}`);
  return response.data;
}

export async function searchResources(query: string): Promise<any> {
  const response = await axios.get(
    `${amethystApiPath}/resources/search?q=${encodeURIComponent(query)}`
  );
  return response.data;
}

