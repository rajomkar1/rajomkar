# Hikaro DM — project context

Instagram comment-to-DM automation SaaS by Hikaro (sole proprietorship, Udyam registered).
Parent domain: hikarohq.com (company site, policies, email hello@hikarohq.com).
Product name: TBD, likely DMkoi, hosted at dmkoi.hikarohq.com (placeholder "Hikaro DM").

## Stack
- TypeScript, Cloudflare Workers + Hono, D1 (Drizzle), KV, R2, Pages (React + Vite + Tailwind)
- Instagram API with Instagram Login, Graph API v27.0
- Private reply: POST graph.instagram.com/v27.0/{ig-id}/messages, recipient.comment_id
- Payments: Razorpay Subscriptions (India), Paddle (abroad)
- Tests: Vitest, Playwright

## Rules
- One small task per session; end with passing tests and a note below.
- Never commit secrets; use `wrangler secret` and `.dev.vars` (gitignored).
- Every DB query scoped to the account (tenant isolation).
- Verify signatures on all webhooks (Meta, Razorpay, Paddle).
- Meta guardrails: <=600 private replies/hour/account, 24h window, no tag-friends.
- Fair-use caps (shared per plan): Free 200/day, Pro 3,000, Business 10,000, Agency 50,000.
- Commit messages: plain developer style, no AI attribution.

## Progress
- Week 0: project skeleton, health route, Meta webhook verification route, test setup.
- Week 1: D1 schema (migrations/0001_init.sql), dev/staging/prod envs in wrangler.toml, GitHub Actions CI, company site with policy pages (site/). Site details filled (add PIN code to address).
- Next (week 2): Instagram login (OAuth), encrypted token storage, webhook signature check.
