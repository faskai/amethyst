'use client';

import AppBar from '@mui/material/AppBar';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';

import { useResponsive } from '@/hooks/use-responsive';
import ModeSwitch from '@/components/ModeSwitch';

import { HEADER, NAV } from '../config-layout';

// ----------------------------------------------------------------------

type Props = {
  onOpenNav?: VoidFunction;
};

export default function Header({ onOpenNav }: Props) {
  const theme = useTheme();
  const lgUp = useResponsive('up', 'lg');

  return (
    <AppBar
      sx={{
        height: HEADER.H_MOBILE,
        zIndex: theme.zIndex.appBar + 1,
        backgroundColor: theme.palette.background.default,
        borderBottom: `1px solid ${theme.palette.divider}`,
        boxShadow: 'none',
        transition: theme.transitions.create(['height'], {
          duration: theme.transitions.duration.shorter,
        }),
        ...(lgUp && {
          width: `calc(100% - ${NAV.W_VERTICAL + 1}px)`,
          height: HEADER.H_DESKTOP,
        }),
      }}
    >
      <Toolbar
        sx={{
          height: 1,
          px: { lg: 5 },
        }}
      >
        {!lgUp && (
          <IconButton onClick={onOpenNav} sx={{ mr: 1 }}>
            <MenuIcon />
          </IconButton>
        )}

        <Stack
          flexGrow={1}
          direction="row"
          alignItems="center"
          justifyContent="flex-end"
          spacing={{ xs: 0.5, sm: 1.5 }}
        >
          <ModeSwitch />
        </Stack>
      </Toolbar>
    </AppBar>
  );
}

