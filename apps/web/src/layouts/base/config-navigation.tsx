import { useMemo } from 'react';

import { paths } from '@/routes/paths';
import Iconify from '@/components/iconify';

// ----------------------------------------------------------------------

const icon = (name: string) => <Iconify icon={name} sx={{ width: 1, height: 1 }} />;

const ICONS = {
  apps: icon('solar:code-bold-duotone'),
};

// ----------------------------------------------------------------------

export function useNavData() {
  const data = useMemo(
    () => [
      {
        subheader: 'General',
        items: [
          { title: 'Apps', path: paths.apps.root, icon: ICONS.apps },
        ],
      },
    ],
    []
  );

  return data;
}

