'use client';

import { useEffect, useState } from 'react';

import DeleteIcon from '@mui/icons-material/Delete';
import {
  Avatar,
  Box,
  Card,
  CircularProgress,
  IconButton,
  Stack,
  Typography,
} from '@mui/material';
import Container from '@mui/material/Container';

import type { Resource } from '@/api/resources';
import { deleteResource, listResources } from '@/api/resources';
import EmptyState from '@/components/empty-state';

export default function ResourcesListView() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadResources = () => {
    setIsLoading(true);
    listResources().then((response) => {
      setResources(response);
      setIsLoading(false);
    });
  };

  useEffect(() => {
    loadResources();
  }, []);

  const handleDelete = async (id: string) => {
    if (!id) return;
    await deleteResource(id);
    loadResources();
  };

  return (
    <Container maxWidth="lg">
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 4 }}>
        <Typography variant="h4">Resources</Typography>
      </Stack>

      {resources.length === 0 ? (
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
              title="No Resources"
              description="Resources will appear here when you add them in your apps."
            />
          )}
        </Box>
      ) : (
        <Stack spacing={2}>
          {resources.map((resource) => (
            <Card
              key={resource.id}
              sx={{
                p: 3,
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                {resource.img_url && (
                  <Avatar
                    src={resource.img_url}
                    alt={resource.name}
                    sx={{ width: 48, height: 48 }}
                    imgProps={{ style: { objectFit: 'contain' } }}
                  />
                )}
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" fontWeight={600}>
                    {resource.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {resource.provider} • {resource.type}
                  </Typography>
                </Box>
                <IconButton
                  color="error"
                  onClick={() => handleDelete(resource.id!)}
                  sx={{ ml: 'auto' }}
                >
                  <DeleteIcon />
                </IconButton>
              </Stack>
            </Card>
          ))}
        </Stack>
      )}
    </Container>
  );
}

