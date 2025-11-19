import { memo, forwardRef } from 'react';

import Box from '@mui/material/Box';

import { ScrollbarProps } from './types';

// ----------------------------------------------------------------------

// Simplified scrollbar component without simplebar-react dependency
const Scrollbar = forwardRef<HTMLDivElement, ScrollbarProps>(({ children, sx, ...other }, ref) => {
  return (
    <Box 
      ref={ref} 
      sx={{ 
        overflow: 'auto',
        height: '100%',
        '&::-webkit-scrollbar': {
          width: 8,
          height: 8,
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: 'rgba(0,0,0,0.2)',
          borderRadius: 4,
        },
        '&::-webkit-scrollbar-thumb:hover': {
          backgroundColor: 'rgba(0,0,0,0.3)',
        },
        ...sx 
      }} 
      {...other}
    >
      {children}
    </Box>
  );
});

export default memo(Scrollbar);

