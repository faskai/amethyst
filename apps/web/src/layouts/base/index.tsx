'use client';

import Box from '@mui/material/Box';

import { useBoolean } from '@/hooks/use-boolean';
import { useResponsive } from '@/hooks/use-responsive';

import Main from './main';
import Header from './header';
import NavVertical from './nav-vertical';

// ----------------------------------------------------------------------

type Props = {
  children: React.ReactNode;
};

export default function BaseLayout({ children }: Props) {
  const lgUp = useResponsive('up', 'lg');
  const nav = useBoolean();

  return (
    <>
      <Header onOpenNav={nav.onTrue} />

      <Box
        sx={{
          minHeight: 1,
          display: 'flex',
          flexDirection: { xs: 'column', lg: 'row' },
        }}
      >
        <NavVertical openNav={nav.value} onCloseNav={nav.onFalse} />

        <Main>{children}</Main>
      </Box>
    </>
  );
}

