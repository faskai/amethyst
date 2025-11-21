'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import AddIcon from '@mui/icons-material/Add';
import { Box, Card, CircularProgress } from '@mui/material';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import { listApps } from '@/api/apps';
import EmptyState from '@/components/empty-state';
import Iconify from '@/components/iconify';
import { paths } from '@/routes/paths';

interface AmtApp {
  id: string;
  files: any[];
  resource_ids: string[];
  workspaceId: string;
}

export default function AppsListView() {
  const router = useRouter();

  const [apps, setApps] = useState<AmtApp[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listApps().then((response) => {
      setApps(response);
      setIsLoading(false);
    });
  }, []);

  return (
    <Container maxWidth="lg">
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 4 }}>
        <Typography variant="h4">Apps</Typography>
        <Button
          variant="contained"
          onClick={() => router.push(paths.apps.create)}
          startIcon={<AddIcon />}
        >
          New App
        </Button>
      </Stack>

      {apps.length === 0 ? (
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="75vh"
          width="100%"
          textAlign="center"
        >
          {isLoading ? (
            <Box sx={{ width: '100%' }}>
              <CircularProgress />
            </Box>
          ) : (
            <EmptyState
              title="No Apps"
              description="Create your first app."
              action={
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => router.push(paths.apps.create)}
                >
                  Create App
                </Button>
              }
            />
          )}
        </Box>
      ) : (
        <Stack spacing={2}>
          {apps.map((app) => {
            const firstFileContent = app.files[0]?.content || '';
            const truncatedContent = firstFileContent.slice(0, 150);
            const shouldTruncate = firstFileContent.length > 150;

            return (
              <Card
                key={app.id}
                sx={{
                  p: 3,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
                onClick={() => router.push(paths.apps.details(app.id))}
              >
                <Stack spacing={1.5}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between">
                    <Typography variant="body2" color="text.secondary">
                      {app.files.length} file{app.files.length !== 1 ? 's' : ''} •{' '}
                      {app.resource_ids.length} resource{app.resource_ids.length !== 1 ? 's' : ''}
                    </Typography>
                    <Iconify icon="eva:arrow-ios-forward-fill" width={20} />
                  </Stack>
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: 'action.hover',
                      borderRadius: 1,
                      overflow: 'hidden',
                    }}
                  >
                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                        fontSize: '0.75rem',
                        whiteSpace: 'pre-wrap',
                        color: 'text.secondary',
                      }}
                    >
                      {truncatedContent}
                      {shouldTruncate && '...'}
                    </Typography>
                  </Box>
                </Stack>
              </Card>
            );
          })}
        </Stack>
      )}
    </Container>
  );
}

