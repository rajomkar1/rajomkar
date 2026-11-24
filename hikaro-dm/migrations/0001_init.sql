-- Core schema. Every tenant-owned table carries account_id; every query must filter on it.

CREATE TABLE accounts (
  id TEXT PRIMARY KEY,
  email TEXT,
  plan TEXT NOT NULL DEFAULT 'free',          -- free | pro | business | agency
  plan_status TEXT NOT NULL DEFAULT 'active',  -- active | trialing | past_due | canceled
  country TEXT,
  referred_by TEXT,                            -- partner id
  created_at INTEGER NOT NULL
);

CREATE TABLE ig_accounts (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  ig_user_id TEXT NOT NULL UNIQUE,
  username TEXT,
  token_enc TEXT NOT NULL,                     -- AES-GCM encrypted access token
  token_expires_at INTEGER,
  status TEXT NOT NULL DEFAULT 'active',       -- active | paused | disconnected
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_ig_accounts_account ON ig_accounts(account_id);

CREATE TABLE automations (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  ig_account_id TEXT NOT NULL REFERENCES ig_accounts(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  trigger TEXT NOT NULL,                       -- comment | story_reply | dm_keyword | live_comment
  media_id TEXT,                               -- NULL = all posts
  keywords TEXT NOT NULL,                      -- JSON array
  config TEXT NOT NULL,                        -- JSON: messages, buttons, follow_gate, public replies
  active INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_automations_ig ON automations(ig_account_id, active);

CREATE TABLE contacts (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  ig_scoped_id TEXT NOT NULL,
  username TEXT,
  email TEXT,
  phone TEXT,
  tags TEXT,                                   -- JSON array
  points INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL,
  UNIQUE (account_id, ig_scoped_id)
);

-- One row per DM sent; comment_id primary key prevents duplicate replies.
CREATE TABLE dm_log (
  comment_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  automation_id TEXT,
  status TEXT NOT NULL,                        -- sent | failed | skipped
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_dm_log_account_day ON dm_log(account_id, created_at);

CREATE TABLE subscriptions (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,                      -- razorpay | paddle
  provider_ref TEXT NOT NULL UNIQUE,
  plan TEXT NOT NULL,
  interval TEXT NOT NULL,                      -- month | year
  status TEXT NOT NULL,
  current_period_end INTEGER,
  created_at INTEGER NOT NULL
);

CREATE TABLE partners (
  id TEXT PRIMARY KEY,
  account_id TEXT REFERENCES accounts(id),
  kind TEXT NOT NULL,                          -- influencer | intern
  code TEXT NOT NULL UNIQUE,
  commission_pct INTEGER NOT NULL DEFAULT 30,
  commission_months INTEGER NOT NULL DEFAULT 12,
  recruited_by TEXT REFERENCES partners(id),   -- intern who recruited this influencer
  override_until INTEGER,
  first_month_price INTEGER,                   -- partner-chosen discount, paise
  created_at INTEGER NOT NULL
);

CREATE TABLE commissions (
  id TEXT PRIMARY KEY,
  partner_id TEXT NOT NULL REFERENCES partners(id),
  account_id TEXT NOT NULL,
  payment_ref TEXT NOT NULL,
  amount INTEGER NOT NULL,                     -- paise / cents
  currency TEXT NOT NULL,
  kind TEXT NOT NULL,                          -- direct | override | topup | bonus
  status TEXT NOT NULL DEFAULT 'held',         -- held | payable | paid | reversed
  release_at INTEGER NOT NULL,                 -- 30-day hold
  created_at INTEGER NOT NULL,
  UNIQUE (partner_id, payment_ref, kind)
);

CREATE TABLE audit_log (
  id TEXT PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT,
  created_at INTEGER NOT NULL
);
