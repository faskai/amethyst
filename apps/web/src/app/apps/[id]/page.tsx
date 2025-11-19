import CreateEditAppView from '@/sections/apps/create-edit-app-view';

export const metadata = {
  title: 'Edit App - Amethyst',
};

interface Props {
  params: Promise<{
    id: string;
  }>;
}

export default async function EditAppPage({ params }: Props) {
  const { id } = await params;
  return <CreateEditAppView id={id} />;
}

