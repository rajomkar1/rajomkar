import { Hono } from 'hono';
import type { Env } from '../index';

export const instagramWebhook = new Hono<{ Bindings: Env }>();

// Meta subscription check: echo hub.challenge when the verify token matches.
instagramWebhook.get('/', (c) => {
  const mode = c.req.query('hub.mode');
  const token = c.req.query('hub.verify_token');
  const challenge = c.req.query('hub.challenge');

  if (mode === 'subscribe' && token && token === c.env.META_WEBHOOK_VERIFY_TOKEN && challenge) {
    return c.text(challenge, 200);
  }
  return c.text('Forbidden', 403);
});

// Event receiver. Signature check and processing arrive in week 2.
instagramWebhook.post('/', (c) => c.text('Not implemented', 501));
