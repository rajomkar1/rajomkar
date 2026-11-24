import { describe, it, expect } from 'vitest';
import app from '../src/index';

const env = { META_APP_SECRET: 'secret', META_WEBHOOK_VERIFY_TOKEN: 'verify-me' };

describe('instagram webhook verification', () => {
  it('returns the challenge for a valid token', async () => {
    const res = await app.request(
      '/webhooks/instagram?hub.mode=subscribe&hub.verify_token=verify-me&hub.challenge=12345',
      {},
      env,
    );
    expect(res.status).toBe(200);
    expect(await res.text()).toBe('12345');
  });

  it('rejects a wrong token', async () => {
    const res = await app.request(
      '/webhooks/instagram?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=12345',
      {},
      env,
    );
    expect(res.status).toBe(403);
  });

  it('health check works', async () => {
    const res = await app.request('/health', {}, env);
    expect(res.status).toBe(200);
  });
});
