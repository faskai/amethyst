'use client';

import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Autocomplete from '@mui/material/Autocomplete';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import * as React from 'react';

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

export default function AppsPage() {
  const [app, setApp] = React.useState<App>({
    files: [{ content: '' }],
    resources: [],
  });
  const [pipedreamApps, setPipedreamApps] = React.useState<PipedreamApp[]>([]);
  const [resourceImages, setResourceImages] = React.useState<Record<string, string>>({});
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<any>(null);
  const [progress, setProgress] = React.useState<string>('');
  const [progressDetails, setProgressDetails] = React.useState<string>('');
  const [oauthRequired, setOauthRequired] = React.useState<any>(null);

  const searchPipedreamApps = async (query: string) => {
    if (!query || query.length < 2) return;
    const res = await fetch(`/api/pipedream/apps?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    setPipedreamApps(data.data || []);
  };

  const addResource = (app_data: PipedreamApp) => {
    if (app.resources.some(r => r.key === app_data.name_slug)) return;
    setApp({ ...app, resources: [...app.resources, { name: app_data.name, key: app_data.name_slug, provider: 'pipedream', type: 'tool' }] });
    if (app_data.img_src) {
      setResourceImages(prev => ({ ...prev, [app_data.name_slug]: app_data.img_src! }));
    }
  };

  const removeResource = (key: string) => {
    setApp({ ...app, resources: app.resources.filter(r => r.key !== key) });
    setResourceImages(prev => {
      const { [key]: _, ...rest } = prev;
      return rest;
    });
  };

  const addFile = () => {
    setApp({
      ...app,
      files: [...app.files, { content: '' }],
    });
  };

  const removeFile = (index: number) => {
    setApp({
      ...app,
      files: app.files.filter((_, i) => i !== index),
    });
  };

  const updateFile = (index: number, value: string) => {
    const updated = [...app.files];
    updated[index].content = value;
    setApp({ ...app, files: updated });
  };

  const runApp = React.useCallback(async () => {
    setLoading(true);
    setResult(null);
    setProgress('');
    setProgressDetails('');
    setOauthRequired(null);

    const response = await fetch('http://localhost:8000/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(app),
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'progress') {
            setProgress(data.message);
          } else if (data.type === 'progress_details') {
            setProgressDetails(data.message);
          } else if (data.type === 'oauth_required') {
            setOauthRequired(data);
            setLoading(false);
          } else if (data.type === 'result') {
            setResult(data.data);
            setLoading(false);
          }
        }
      }
    }
  }, [app]);

  const isValid = app.files.every((f) => f.content);

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
          Create Your App
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Build powerful workflows by organizing logic into multiple files
        </Typography>
      </Box>

      <Stack spacing={4}>
        <Box>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Resources</Typography>
          <Autocomplete
            options={pipedreamApps}
            getOptionLabel={(option) => option.name}
            value={null}
            onInputChange={(_, value) => searchPipedreamApps(value)}
            onChange={(_, value) => value && addResource(value)}
            renderOption={(props, option) => {
              const { key, ...otherProps } = props;
              return (
                <Box component="li" key={key} {...otherProps} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  {option.img_src && (
                    <Box component="img" src={option.img_src} alt={option.name} sx={{ width: 24, height: 24 }} />
                  )}
                  <Typography>{option.name}</Typography>
                </Box>
              );
            }}
            renderInput={(params) => <TextField {...params} label="Search Apps" placeholder="Type to search..." />}
            sx={{ mb: 2 }}
          />
          {app.resources.length > 0 && (
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {app.resources.map((resource, idx) => (
                <Chip 
                  key={`${resource.key}-${idx}`} 
                  avatar={resource.key && resourceImages[resource.key] ? <Avatar src={resourceImages[resource.key]} alt={resource.name} /> : undefined}
                  label={resource.name} 
                  onDelete={() => removeResource(resource.key!)} 
                  color="primary" 
                  variant="outlined" 
                />
              ))}
            </Stack>
          )}
        </Box>

        <Divider />

        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Files
            </Typography>
            <Chip label={`${app.files.length} file${app.files.length !== 1 ? 's' : ''}`} size="small" />
          </Box>

          <Stack spacing={3}>
            {app.files.map((file, index) => (
              <Paper key={index} variant="outlined" sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 60 }}>
                    File {index + 1}
                  </Typography>
                  {app.files.length > 1 && (
                    <IconButton
                      onClick={() => removeFile(index)}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>

                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  placeholder="Write your Amethyst code here..."
                  value={file.content}
                  onChange={(e) => updateFile(index, e.target.value)}
                  variant="outlined"
                  helperText="Write agents and functions in Amethyst syntax"
                  sx={{ fontFamily: 'monospace' }}
                />
              </Paper>
            ))}
          </Stack>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={addFile}
            size="large"
          >
            Add Another File
          </Button>

          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
            onClick={runApp}
            disabled={!isValid}
            size="large"
          >
            {loading ? 'Running...' : 'Run App'}
          </Button>
        </Box>

        {progress && (
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Progress
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography
              variant="body2"
              sx={{
                fontFamily: 'monospace',
                color: 'text.secondary',
                fontSize: '0.875rem',
              }}
            >
              {progress}
            </Typography>
            {progressDetails && (
              <Typography
                variant="caption"
                sx={{
                  fontFamily: 'monospace',
                  color: 'text.disabled',
                  fontSize: '0.75rem',
                  mt: 1,
                  display: 'block',
                }}
              >
                {progressDetails}
              </Typography>
            )}
          </Paper>
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
                >
                  Authorize {resource.name}
                </Button>
              ))}
            </Stack>
          </Paper>
        )}

        {result && (
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Results
            </Typography>
            <Divider sx={{ mb: 3 }} />
            
            {result.status === 'completed' && result.memory && (
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  bgcolor: 'action.hover',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  overflowX: 'auto',
                }}
              >
                {JSON.stringify(result.memory, null, 2)}
              </Paper>
            )}
          </Paper>
        )}
      </Stack>
    </Container>
  );
}
