import { PipedreamClient } from '@pipedream/sdk';
import { NextRequest, NextResponse } from 'next/server';

const pd = new PipedreamClient({
  projectEnvironment: process.env.PIPEDREAM_ENVIRONMENT as any,
  clientId: process.env.PIPEDREAM_CLIENT_ID!,
  clientSecret: process.env.PIPEDREAM_CLIENT_SECRET!,
  projectId: process.env.PIPEDREAM_PROJECT_ID!,
});

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const query = searchParams.get('q');

  if (!query) {
    return NextResponse.json({ error: 'Query parameter required' }, { status: 400 });
  }

  const apps = await pd.apps.list({ q: query });
  const mappedApps = apps.data.map((app: any) => ({
    name_slug: app.nameSlug,
    name: app.name,
    img_src: app.imgSrc,
  }));
  return NextResponse.json({ data: mappedApps });
}

