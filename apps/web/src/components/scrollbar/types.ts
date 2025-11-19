import { Theme, SxProps } from '@mui/material/styles';
import { BoxProps } from '@mui/material/Box';

// ----------------------------------------------------------------------

export interface ScrollbarProps extends BoxProps {
  children?: React.ReactNode;
  sx?: SxProps<Theme>;
}

