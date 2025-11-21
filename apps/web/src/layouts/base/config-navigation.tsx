import { useMemo } from 'react';

import Iconify from '@/components/iconify';
import { paths } from '@/routes/paths';

// ----------------------------------------------------------------------

const icon = (name: string) => <Iconify icon={name} sx={{ width: 1, height: 1 }} />;

const ICONS = {
  apps: icon('solar:code-bold-duotone'),
  resources: icon('solar:widget-bold-duotone'),
};

// ----------------------------------------------------------------------

export function useNavData() {
  const data = useMemo(
    () => [
      {
        subheader: 'General',
        items: [
          { title: 'Apps', path: paths.apps.root, icon: ICONS.apps },
          { title: 'Resources', path: paths.resources.root, icon: ICONS.resources },
        ],
      },
    ],
    []
  );

  return data;
}

