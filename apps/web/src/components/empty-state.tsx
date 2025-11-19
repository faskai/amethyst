import Box from '@mui/material/Box';
import Stack, { StackProps } from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

type EmptyStateProps = StackProps & {
  title?: string;
  description?: string;
  action?: React.ReactNode;
};

export default function EmptyState({
  title,
  description,
  action,
  sx,
  ...other
}: EmptyStateProps) {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      sx={{
        px: 3,
        py: 8,
        textAlign: 'center',
        ...sx,
      }}
      {...other}
    >
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          bgcolor: 'action.hover',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h1" sx={{ fontSize: 48, opacity: 0.3 }}>
          📦
        </Typography>
      </Box>

      {title && (
        <Typography variant="h6" sx={{ mb: 1, color: 'text.secondary' }}>
          {title}
        </Typography>
      )}

      {description && (
        <Typography variant="body2" sx={{ color: 'text.disabled', mb: 2 }}>
          {description}
        </Typography>
      )}

      {action && <Box sx={{ mt: 2 }}>{action}</Box>}
    </Stack>
  );
}

