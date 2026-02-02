CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  id UUID PRIMARY KEY,
  username TEXT
);

CREATE TABLE businesses (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title TEXT
);

CREATE TABLE chats (
  id UUID PRIMARY KEY,
  business_id UUID REFERENCES businesses(id),
  user_id UUID REFERENCES users(id)
);

CREATE INDEX idx_business_user ON businesses(user_id);
CREATE INDEX idx_chat_business ON chats(business_id);
