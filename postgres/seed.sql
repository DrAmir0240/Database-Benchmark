INSERT INTO users
SELECT gen_random_uuid(), md5(random()::text)
FROM generate_series(1,10000);

INSERT INTO businesses
SELECT gen_random_uuid(), u.id, md5(random()::text)
FROM users u, generate_series(1,5);

INSERT INTO chats
SELECT gen_random_uuid(), b.id, b.user_id
FROM businesses b, generate_series(1,10);
