import axios from 'axios';

import { amethystApiPath } from './api-constants';

export async function createApp() {
  const res = await axios.post(`${amethystApiPath}/apps/`);
  return res.data;
}

export async function getApp(id: string) {
  const res = await axios.get(`${amethystApiPath}/apps/${id}`);
  return res.data;
}

export async function updateApp(id: string, userMessage: string) {
  const res = await axios.patch(`${amethystApiPath}/apps/${id}`, {
    userMessage,
  });
  return res.data;
}

interface AppRunCallbacks {
  onProgress?: (message: string) => void;
  onTaskCreated?: (task: any) => void;
  onAiIntermediateOutput?: (delta: string) => void;
  onTaskUpdated?: (task: any) => void;
  onOauthRequired?: (data: any) => void;
}

interface App {
  files: any[];
  resources: any[];
  workspaceId?: string;
}

const processLine = (line: string, callbacks: AppRunCallbacks) => {
  if (!line.startsWith('data: ')) return;

  const data = JSON.parse(line.slice(6));

  if (data.type === 'progress' && callbacks.onProgress) {
    callbacks.onProgress(data.message);
  } else if (data.type === 'task_created' && callbacks.onTaskCreated) {
    callbacks.onTaskCreated(data.task);
  } else if (data.type === 'ai_intermediate_output' && callbacks.onAiIntermediateOutput) {
    callbacks.onAiIntermediateOutput(data.delta);
  } else if (data.type === 'task_updated' && callbacks.onTaskUpdated) {
    callbacks.onTaskUpdated(data.task);
  } else if (data.type === 'oauth_required' && callbacks.onOauthRequired) {
    callbacks.onOauthRequired(data);
  }
};

const readStream = async (
  reader: ReadableStreamDefaultReader<Uint8Array>,
  decoder: TextDecoder,
  buffer: string,
  callbacks: AppRunCallbacks
): Promise<void> => {
  const { done, value } = await reader.read();
  if (done) return;

  const newBuffer = buffer + decoder.decode(value, { stream: true });
  const lines = newBuffer.split('\n');
  const remainingBuffer = lines.pop() || '';

  lines.forEach((line) => processLine(line, callbacks));

  return readStream(reader, decoder, remainingBuffer, callbacks);
};

export async function createAppApi(app: any, workspaceId: string = 'default') {
  const payload: App = {
    files: app.files.map((f: any) => ({ content: f.content })),
    resources: app.resources,
    workspaceId,
  };

  const response = await axios.post(`${amethystApiPath}/apps/`, payload);
  return response.data;
}

export async function runApp(appId: string, callbacks: AppRunCallbacks = {}) {
  const response = await fetch(`${amethystApiPath}/apps/${appId}/runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  await readStream(reader, decoder, '', callbacks);
}

export async function getRun(appId: string, runId: string) {
  const response = await axios.get(`${amethystApiPath}/apps/${appId}/runs/${runId}`);
  return response.data;
}

export async function listApps() {
  const response = await axios.get(`${amethystApiPath}/apps/`);
  return response.data;
}

export async function getAppById(appId: string) {
  const response = await axios.get(`${amethystApiPath}/apps/${appId}`);
  return response.data;
}

