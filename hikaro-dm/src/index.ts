import { Hono } from 'hono';
import { instagramWebhook } from './routes/webhook';

export type Env = {
  META_APP_SECRET: string;
  META_WEBHOOK_VERIFY_TOKEN: string;
};

const app = new Hono<{ Bindings: Env }>();

app.get('/health', (c) => c.json({ ok: true }));
app.route('/webhooks/instagram', instagramWebhook);

export default app;
