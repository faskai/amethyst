'use client';

import { useCallback, useEffect, useState } from 'react';

import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Collapse from '@mui/material/Collapse';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import { createAppApi, getAppById, runApp as runAppApi } from '@/api/apps';
import { searchApps } from '@/api/workflow';
import Iconify from '@/components/iconify';
import type { MentionResource } from '@/components/mention-text-field';
import MentionTextField from '@/components/mention-text-field';

interface AmtFile {
  content: string;
}

interface Resource {
  name: string;
  provider: string;
  type: string;
  key?: string;
}

interface App {
  files: AmtFile[];
  resources: Resource[];
}

interface PipedreamApp {
  name_slug: string;
  name: string;
  img_src?: string;
}

interface Task {
  id: string;
  parent_task_id: string | null;
  resource_name: string;
  task_type: string;
  input: any;
  result: any;
  ai_calls?: Array<{
    input_messages: any[];
    intermediate_outputs: any[];
  }>;
}

interface TaskWithChildren extends Task {
  children: TaskWithChildren[];
}

interface Props {
  id?: string;
}

export default function CreateEditAppView({ id }: Props) {
  const [app, setApp] = useState<App>({
    files: [{ content: '' }],
    resources: [],
  });
  const [appId, setAppId] = useState<string | null>(null);
  const [selectedFileIndex, setSelectedFileIndex] = useState(0);
  const [resourceImages, setResourceImages] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<string>('');
  const [oauthRequired, setOauthRequired] = useState<any>(null);
  const [tasks, setTasks] = useState<Map<string, Task>>(new Map());
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentDelta, setCurrentDelta] = useState<string>('');
  const [aiCallsExpanded, setAiCallsExpanded] = useState<boolean>(false);
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());

  // Load app data if id is provided
  useEffect(() => {
    if (id) {
      getAppById(id).then((appData) => {
        setApp({
          files: appData.files || [{ content: '' }],
          resources: appData.resources || [],
        });
        setAppId(id);

        // Load previous tasks from memory
        if (appData.memory && appData.memory.tasks) {
          const tasksMap = new Map<string, Task>();
          Object.entries(appData.memory.tasks).forEach(([taskId, task]: [string, any]) => {
            tasksMap.set(taskId, {
              id: task.id,
              parent_task_id: task.parent_task_id,
              resource_name: task.resource_name,
              task_type: task.task_type,
              input: task.input,
              result: task.result,
              ai_calls: task.ai_calls,
            });
          });
          setTasks(tasksMap);

          // Auto-expand root tasks
          const rootTasks = Array.from(tasksMap.values()).filter(
            (t) => !t.parent_task_id || !tasksMap.has(t.parent_task_id)
          );
          setExpandedTasks(new Set(rootTasks.map((t) => t.id)));
        }

        // Load resource images
        const images: Record<string, string> = {};
        appData.resources?.forEach((resource: any) => {
          if (resource.key) {
            // You might need to fetch the image URL from pipedream API
            // For now, we'll just store what we have
          }
        });
        setResourceImages(images);
      });
    }
  }, [id]);

  const removeResource = (key: string) => {
    setApp({ ...app, resources: app.resources.filter((r) => r.key !== key) });
    setResourceImages((prev) => {
      const { [key]: _, ...rest } = prev;
      return rest;
    });
  };

  const addFile = () => {
    setApp({
      ...app,
      files: [...app.files, { content: '' }],
    });
    setSelectedFileIndex(app.files.length);
  };

  const removeFile = (index: number) => {
    if (app.files.length === 1) return;
    setApp({
      ...app,
      files: app.files.filter((_, i) => i !== index),
    });
    if (selectedFileIndex >= app.files.length - 1) {
      setSelectedFileIndex(Math.max(0, app.files.length - 2));
    }
  };

  const updateFileContent = (index: number, content: string) => {
    const updated = [...app.files];
    updated[index].content = content;
    setApp({ ...app, files: updated });
  };

  const buildTaskTree = useCallback((tasksMap: Map<string, Task>): TaskWithChildren[] => {
    const taskArray = Array.from(tasksMap.values());
    const roots: TaskWithChildren[] = [];
    const taskWithChildrenMap = new Map<string, TaskWithChildren>();

    // Initialize all tasks with empty children array
    taskArray.forEach((task) => {
      taskWithChildrenMap.set(task.id, { ...task, children: [] });
    });

    // Build tree structure
    taskArray.forEach((task) => {
      const taskWithChildren = taskWithChildrenMap.get(task.id)!;
      if (task.parent_task_id && taskWithChildrenMap.has(task.parent_task_id)) {
        taskWithChildrenMap.get(task.parent_task_id)!.children.push(taskWithChildren);
      } else {
        roots.push(taskWithChildren);
      }
    });

    return roots;
  }, []);

  const toggleTaskExpanded = (taskId: string) => {
    setExpandedTasks((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const getTaskIcon = (taskType: string) => {
    switch (taskType) {
      case 'amt_agent':
        return 'solar:user-speak-rounded-bold-duotone';
      case 'amt_function':
        return 'solar:code-bold-duotone';
      case 'statement':
        return 'solar:document-text-bold-duotone';
      default:
        return 'solar:widget-bold-duotone';
    }
  };

  const getTaskStatus = (task: Task) => {
    if (task.result !== null) return 'completed';
    if (task.id === currentTaskId) return 'running';
    return 'pending';
  };

  const renderTaskTreeItem = (task: TaskWithChildren, depth: number = 0) => {
    const hasChildren = task.children.length > 0;
    const isExpanded = expandedTasks.has(task.id);
    const status = getTaskStatus(task);
    const isCurrentTask = task.id === currentTaskId;

    return (
      <Box key={task.id}>
        <ListItemButton
          selected={isCurrentTask}
          onClick={() => setCurrentTaskId(task.id)}
          sx={{
            pl: 2 + depth * 3,
            py: 0.75,
            bgcolor: isCurrentTask ? 'action.selected' : 'transparent',
            '&:hover': { bgcolor: isCurrentTask ? 'action.selected' : 'action.hover' },
          }}
        >
          {hasChildren && (
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                toggleTaskExpanded(task.id);
              }}
              sx={{ mr: 0.5 }}
            >
              <Iconify
                icon={
                  isExpanded
                    ? 'solar:alt-arrow-down-bold-duotone'
                    : 'solar:alt-arrow-right-bold-duotone'
                }
                width={16}
              />
            </IconButton>
          )}
          <ListItemIcon sx={{ minWidth: 32 }}>
            {status === 'running' ? (
              <CircularProgress size={16} />
            ) : (
              <Iconify icon={getTaskIcon(task.task_type)} width={18} />
            )}
          </ListItemIcon>
          <ListItemText
            primary={task.resource_name || task.task_type}
            primaryTypographyProps={{
              variant: 'body2',
              sx: {
                fontWeight: isCurrentTask ? 600 : 400,
                color: status === 'completed' ? 'text.secondary' : 'text.primary',
              },
            }}
          />
          {status === 'completed' && (
            <Iconify icon="solar:check-circle-bold-duotone" width={16} color="success.main" />
          )}
        </ListItemButton>
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            {task.children.map((child) => renderTaskTreeItem(child, depth + 1))}
          </Collapse>
        )}
      </Box>
    );
  };

  const runApp = useCallback(async () => {
    setLoading(true);
    setProgress('');
    setOauthRequired(null);
    setCurrentTaskId(null);
    setCurrentDelta('');

    try {
      // Create app if not exists
      let currentAppId: string;
      if (!appId) {
        const result = await createAppApi(app, 'default');
        currentAppId = result.id;
        setAppId(currentAppId);
      } else {
        currentAppId = appId;
      }

      await runAppApi(currentAppId, {
        onProgress: (message) => setProgress(message),
        onTaskCreated: (task: Task) => {
          setTasks((prev) => new Map(prev).set(task.id, task));
          setCurrentTaskId(task.id);
          setCurrentDelta('');
          // Auto-expand parent task
          if (task.parent_task_id) {
            setExpandedTasks((prev) => new Set(prev).add(task.parent_task_id!));
          }
        },
        onAiIntermediateOutput: (delta: string) => {
          setCurrentDelta(delta);
        },
        onTaskUpdated: (task: Task) => {
          setTasks((prev) => {
            const newMap = new Map(prev);
            newMap.set(task.id, task);
            return newMap;
          });
        },
        onOauthRequired: (data) => {
          setOauthRequired(data);
          setLoading(false);
        },
      });
    } finally {
      setLoading(false);
    }
  }, [app, appId]);

  const rerunApp = useCallback(async () => {
    if (!appId) return;

    setLoading(true);
    setProgress('');
    setOauthRequired(null);
    setCurrentTaskId(null);
    setCurrentDelta('');

    try {
      await runAppApi(appId, {
        onProgress: (message) => setProgress(message),
        onTaskCreated: (task: Task) => {
          setTasks((prev) => new Map(prev).set(task.id, task));
          setCurrentTaskId(task.id);
          setCurrentDelta('');
          if (task.parent_task_id) {
            setExpandedTasks((prev) => new Set(prev).add(task.parent_task_id!));
          }
        },
        onAiIntermediateOutput: (delta: string) => {
          setCurrentDelta(delta);
        },
        onTaskUpdated: (task: Task) => {
          setTasks((prev) => {
            const newMap = new Map(prev);
            newMap.set(task.id, task);
            return newMap;
          });
        },
        onOauthRequired: (data) => {
          setOauthRequired(data);
          setLoading(false);
        },
      });
    } finally {
      setLoading(false);
    }
  }, [appId]);

  const isValid = app.files.every((f) => f.content.trim());

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Stack spacing={3}>
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Apps
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Build powerful workflows with multi-file projects
          </Typography>
        </Box>

        {app.resources.length > 0 && (
          <Box>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Resources
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {app.resources.map((resource, idx) => (
                <Chip
                  key={`${resource.key}-${idx}`}
                  avatar={
                    resource.key && resourceImages[resource.key] ? (
                      <Avatar
                        src={resourceImages[resource.key]}
                        alt={resource.name}
                        sx={{ width: 32, height: 32 }}
                        imgProps={{ style: { objectFit: 'contain' } }}
                      />
                    ) : undefined
                  }
                  label={resource.name}
                  onDelete={() => removeResource(resource.key!)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Stack>
          </Box>
        )}

        {app.resources.length > 0 && <Divider />}

        <Box sx={{ display: 'flex', gap: 3, minHeight: 500 }}>
          {/* Left Sidebar - File List */}
          <Paper
            variant="outlined"
            sx={{ width: 280, flexShrink: 0, display: 'flex', flexDirection: 'column' }}
          >
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Files ({app.files.length})
              </Typography>
            </Box>
            <List sx={{ flex: 1, overflow: 'auto', p: 0 }}>
              {app.files.map((file, index) => (
                <ListItemButton
                  key={index}
                  selected={selectedFileIndex === index}
                  onClick={() => setSelectedFileIndex(index)}
                  sx={{
                    py: 1.5,
                    px: 2,
                    borderBottom: 1,
                    borderColor: 'divider',
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <Iconify icon="solar:document-bold-duotone" width={20} />
                  </ListItemIcon>
                  <ListItemText
                    primary={`file-${index + 1}.amt`}
                    primaryTypographyProps={{
                      variant: 'body2',
                      sx: { fontFamily: 'monospace' },
                    }}
                  />
                  {app.files.length > 1 && (
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(index);
                      }}
                      sx={{ ml: 1 }}
                    >
                      <Iconify icon="solar:trash-bin-minimalistic-bold-duotone" width={20} />
                    </IconButton>
                  )}
                </ListItemButton>
              ))}
            </List>
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Button
                fullWidth
                variant="outlined"
                size="small"
                startIcon={<Iconify icon="solar:add-circle-bold-duotone" />}
                onClick={addFile}
              >
                New File
              </Button>
            </Box>
          </Paper>

          {/* Right Side - File Editor */}
          <Paper variant="outlined" sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'text.secondary' }}>
                {`file-${selectedFileIndex + 1}.amt`}
              </Typography>
            </Box>
            <Box sx={{ flex: 1, p: 0 }}>
              <MentionTextField
                value={app.files[selectedFileIndex]?.content || ''}
                onChange={(content) => updateFileContent(selectedFileIndex, content)}
                onSearch={async (query: string) => {
                  const results = await searchApps(query);
                  return results.map((r: PipedreamApp) => ({
                    id: r.name_slug,
                    name: r.name,
                    key: r.name_slug,
                    type: 'tool',
                    provider: 'pipedream',
                    img_src: r.img_src,
                  }));
                }}
                onResourceSelect={(resource: MentionResource) => {
                  // Add to resources if not already there
                  if (!app.resources.some((r) => r.key === resource.key)) {
                    setApp({
                      ...app,
                      resources: [
                        ...app.resources,
                        {
                          name: resource.name,
                          key: resource.key!,
                          provider: resource.provider || 'pipedream',
                          type: resource.type || 'tool',
                        },
                      ],
                    });
                    if (resource.img_src) {
                      setResourceImages((prev) => ({
                        ...prev,
                        [resource.key!]: resource.img_src!,
                      }));
                    }
                  }
                }}
                getImageUrl={(resource: MentionResource) =>
                  resource.key ? resourceImages[resource.key] : undefined
                }
                existingResources={app.resources.map((r) => ({
                  id: r.key || '',
                  name: r.name,
                  key: r.key,
                  type: r.type,
                  provider: r.provider,
                  img_src: r.key ? resourceImages[r.key] : undefined,
                }))}
                placeholder="Write your Amethyst code here... (type 'use @app_name' to search and add other apps)"
              />
            </Box>
          </Paper>
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={
              loading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <Iconify icon="solar:play-bold-duotone" />
              )
            }
            onClick={runApp}
            disabled={!isValid || loading}
          >
            {loading ? 'Running...' : 'Run App'}
          </Button>
          {appId && (
            <Button
              variant="outlined"
              size="large"
              startIcon={<Iconify icon="solar:restart-bold-duotone" />}
              onClick={rerunApp}
            >
              Rerun
            </Button>
          )}
        </Box>

        {(loading || tasks.size > 0) && (
          <Box sx={{ display: 'flex', gap: 3, minHeight: 500 }}>
            {/* Left Panel - Task Hierarchy */}
            <Paper
              variant="outlined"
              sx={{ width: 350, flexShrink: 0, display: 'flex', flexDirection: 'column' }}
            >
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Task Trace
                </Typography>
                {progress && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: 'block' }}
                  >
                    {progress}
                  </Typography>
                )}
              </Box>
              <List sx={{ flex: 1, overflow: 'auto', p: 0 }}>
                {buildTaskTree(tasks).map((task) => renderTaskTreeItem(task))}
              </List>
            </Paper>

            {/* Right Panel - Task Details */}
            <Paper
              variant="outlined"
              sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 3 }}
            >
              {currentTaskId && tasks.has(currentTaskId) ? (
                <>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Task Details
                  </Typography>
                  <Divider sx={{ mb: 2 }} />

                  {(() => {
                    const currentTask = tasks.get(currentTaskId)!;
                    const status = getTaskStatus(currentTask);

                    return (
                      <Stack spacing={2}>
                        {/* Task Info */}
                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mb: 0.5 }}
                          >
                            Name
                          </Typography>
                          <Typography variant="body2" fontWeight={500}>
                            {currentTask.resource_name || currentTask.task_type}
                          </Typography>
                        </Box>

                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mb: 0.5 }}
                          >
                            Type
                          </Typography>
                          <Chip label={currentTask.task_type} size="small" variant="outlined" />
                        </Box>

                        <Box>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mb: 0.5 }}
                          >
                            Status
                          </Typography>
                          <Chip
                            label={status}
                            size="small"
                            color={(() => {
                              if (status === 'completed') return 'success';
                              if (status === 'running') return 'primary';
                              return 'default';
                            })()}
                          />
                        </Box>

                        {/* Current Delta (for running tasks) */}
                        {status === 'running' && currentDelta && (
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'action.hover' }}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mb: 1 }}
                            >
                              Current Output
                            </Typography>
                            <Typography
                              variant="body2"
                              sx={{
                                fontFamily: 'monospace',
                                fontSize: '0.75rem',
                                whiteSpace: 'pre-wrap',
                              }}
                            >
                              {currentDelta}
                            </Typography>
                          </Paper>
                        )}

                        {/* Task Input */}
                        {currentTask.input && Object.keys(currentTask.input).length > 0 && (
                          <Box>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mb: 1 }}
                            >
                              Input
                            </Typography>
                            <Paper
                              variant="outlined"
                              sx={{ p: 1.5, bgcolor: 'background.neutral' }}
                            >
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: 'monospace',
                                  fontSize: '0.75rem',
                                  whiteSpace: 'pre-wrap',
                                }}
                              >
                                {JSON.stringify(currentTask.input, null, 2)}
                              </Typography>
                            </Paper>
                          </Box>
                        )}

                        {/* Task Result */}
                        {currentTask.result !== null && (
                          <Box>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mb: 1 }}
                            >
                              Result
                            </Typography>
                            <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'success.lighter' }}>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontFamily: 'monospace',
                                  fontSize: '0.75rem',
                                  whiteSpace: 'pre-wrap',
                                }}
                              >
                                {typeof currentTask.result === 'string'
                                  ? currentTask.result
                                  : JSON.stringify(currentTask.result, null, 2)}
                              </Typography>
                            </Paper>
                          </Box>
                        )}

                        {/* AI Calls */}
                        {currentTask.ai_calls && currentTask.ai_calls.length > 0 && (
                          <Box>
                            <Box
                              sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                                mb: 1,
                                cursor: 'pointer',
                              }}
                              onClick={() => setAiCallsExpanded(!aiCallsExpanded)}
                            >
                              <Iconify
                                icon={
                                  aiCallsExpanded
                                    ? 'eva:chevron-down-fill'
                                    : 'eva:chevron-right-fill'
                                }
                                width={20}
                              />
                              <Typography variant="caption" color="text.secondary">
                                AI Calls ({currentTask.ai_calls.length})
                              </Typography>
                            </Box>
                            <Collapse in={aiCallsExpanded}>
                              <Stack spacing={2}>
                                {currentTask.ai_calls.map((aiCall, idx) => (
                                  <Paper
                                    key={idx}
                                    variant="outlined"
                                    sx={{ p: 1.5, bgcolor: 'grey.50' }}
                                  >
                                    <Stack spacing={1.5}>
                                      {/* AI Call Header */}
                                      <Typography
                                        variant="caption"
                                        fontWeight="bold"
                                        color="text.secondary"
                                      >
                                        AI Call #{idx + 1}
                                      </Typography>

                                      {/* Input Messages */}
                                      {aiCall.input_messages &&
                                        aiCall.input_messages.length > 0 && (
                                          <Box>
                                            <Typography
                                              variant="caption"
                                              color="text.disabled"
                                              sx={{ display: 'block', mb: 0.5 }}
                                            >
                                              Input Messages
                                            </Typography>
                                            <Paper
                                              variant="outlined"
                                              sx={{ p: 1, bgcolor: 'grey.100' }}
                                            >
                                              <Typography
                                                variant="body2"
                                                sx={{
                                                  fontFamily: 'monospace',
                                                  fontSize: '0.7rem',
                                                  whiteSpace: 'pre-wrap',
                                                  color: 'text.secondary',
                                                }}
                                              >
                                                {JSON.stringify(aiCall.input_messages, null, 2)}
                                              </Typography>
                                            </Paper>
                                          </Box>
                                        )}

                                      {/* Intermediate Outputs */}
                                      {aiCall.intermediate_outputs &&
                                        aiCall.intermediate_outputs.length > 0 && (
                                          <Box>
                                            <Typography
                                              variant="caption"
                                              color="text.disabled"
                                              sx={{ display: 'block', mb: 0.5 }}
                                            >
                                              Intermediate Outputs
                                            </Typography>
                                            <Paper
                                              variant="outlined"
                                              sx={{ p: 1, bgcolor: 'grey.200' }}
                                            >
                                              <Typography
                                                variant="body2"
                                                sx={{
                                                  fontFamily: 'monospace',
                                                  fontSize: '0.7rem',
                                                  whiteSpace: 'pre-wrap',
                                                  color: 'text.secondary',
                                                }}
                                              >
                                                {JSON.stringify(
                                                  aiCall.intermediate_outputs,
                                                  null,
                                                  2
                                                )}
                                              </Typography>
                                            </Paper>
                                          </Box>
                                        )}
                                    </Stack>
                                  </Paper>
                                ))}
                              </Stack>
                            </Collapse>
                          </Box>
                        )}
                      </Stack>
                    );
                  })()}
                </>
              ) : (
                <Box
                  sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}
                >
                  <Typography color="text.secondary">Select a task to view details</Typography>
                </Box>
              )}
            </Paper>
          </Box>
        )}

        {oauthRequired && (
          <Paper variant="outlined" sx={{ p: 3, bgcolor: 'warning.lighter' }}>
            <Typography variant="h6" gutterBottom fontWeight={600} color="warning.dark">
              Authorization Required
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              {oauthRequired.resources?.map((resource: any, idx: number) => (
                <Button
                  key={idx}
                  variant="contained"
                  color="warning"
                  href={resource.auth_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  fullWidth
                  startIcon={
                    resource.key && resourceImages[resource.key] ? (
                      <Avatar
                        src={resourceImages[resource.key]}
                        alt={resource.name}
                        sx={{ width: 24, height: 24 }}
                      />
                    ) : undefined
                  }
                >
                  Authorize {resource.name}
                </Button>
              ))}
            </Stack>
          </Paper>
        )}
      </Stack>
    </Container>
  );
}

