# 📝 DB Benchmark
<div dir="rtl">
 بنچمارک برای **MongoDB** و **PostgreSQL** است.  
هدف بررسی عملکرد دیتابیس‌ها روی ۸ کوئری استاندارد و مقایسه avg/p95/max زمان اجرای هر کوئری است.

---

## 🚀 پیش‌نیازها

قبل از شروع، ابزارهای زیر باید نصب باشند:

- Python ≥ 3.12  
- Node.js ≥ 18 (برای بخش seed MongoDB / Node)  
- PostgreSQL ≥ 16  
- MongoDB ≥ 7  
- pipenv یا venv برای مدیریت محیط مجازی Python  
- `psycopg` (برای PostgreSQL)  
- `pymongo` (برای MongoDB)  
- `nanoid` (برای تولید شناسه تصادفی)  

---

## 1️⃣ کلون کردن پروژه و رفتن به مسیر

```bash
git clone <repo-url>
cd db-benchmark
```

## 2️⃣ نصب محیط مجازی Python و وابستگی‌ها
ساخت محیط مجازی
```bash
python -m venv venv
source venv/bin/activate    # Linux/MacOS
# venv\Scripts\activate     # Windows
```

نصب وابستگی‌ها
```bash
pip install pymongo psycopg[binary] nanoid
```

## 3️⃣ نصب و اجرای Docker (اختیاری)
اگر میخوای دیتابیس‌ها در Docker اجرا بشن:
```bash
docker-compose up -d
```
⚠️ اگر از سرویس محلی استفاده می‌کنید، مطمئن شوید MongoDB و PostgreSQL فعال هستند.

## 4️⃣ ایجاد و seed دیتابیس‌ها
این مرحله دیتابیس‌ها را پاکسازی کامل می‌کند، جدول‌ها / collections را ایجاد می‌کند و داده‌های اولیه را می‌ریزد:
```bash
python benchmark/init_db.py
```
✅ پس از اجرا، خروجی باید:
```bash
✅ Databases fully reset and initialized.
```

## 5️⃣ تست دستی (اختیاری)
MongoDB
```bash
mongo
use bench
db.users.find().pretty()
db.businesses.find().pretty()
db.chats.find().pretty()
```
PostgreSQL
```bash
psql -h localhost -U bench -d bench
\dt          # مشاهده جداول
SELECT * FROM users;
SELECT * FROM businesses;
SELECT * FROM chats;
```
## 6️⃣ اجرای بنچمارک
قبل از اجرای runner.py مطمئن شو محیط مجازی فعال است:
```bash
source venv/bin/activate    # Linux/MacOS
```
سپس بنچمارک را اجرا کن:
```bash
python benchmark/runner.py
```

✅ خروجی نمونه:

```bash
{
  "mongo": {
    "q1_all_users": {"avg_ms": 10.5, "p95_ms": 12.1, "max_ms": 15.2},
    "q2_all_businesses": {"avg_ms": 12.0, "p95_ms": 14.3, "max_ms": 16.7},
    "q3_all_chats": {"avg_ms": 9.8, "p95_ms": 11.2, "max_ms": 13.0},
    "q4_users_count": {...},
    "q5_businesses_count": {...},
    "q6_chats_count": {...},
    "q7_user_businesses": {...},
    "q8_business_chats": {...}
  },
  "postgres": {
    "q1_all_users": {"avg_ms": 0.12, "p95_ms": 0.15, "max_ms": 0.18},
    "q2_all_businesses": {"avg_ms": 0.14, "p95_ms": 0.17, "max_ms": 0.21},
    "q3_all_chats": {"avg_ms": 0.11, "p95_ms": 0.13, "max_ms": 0.16},
    "q4_users_count": {...},
    "q5_businesses_count": {...},
    "q6_chats_count": {...},
    "q7_user_businesses": {...},
    "q8_business_chats": {...}
  }
}
```
تمام ۸ کوئری استاندارد روی همه رکوردها اجرا می‌شوند.

## 7️⃣ نکات مهم
### اجرای init_db.py قبل از runner.py ضروری است تا دیتابیس‌ها پاک و seed شوند.

### runner.py روی همه رکوردها کار می‌کند، بنابراین برای دیتابیس‌های بزرگ زمان اجرا طولانی خواهد بود.

### اگر دیتابیس‌ها در Docker هستند، می‌توان با دستور زیر آنها را متوقف کرد:
```bash
docker-compose down
```
### مطمئن شوید psycopg و pymongo با نسخه Python شما سازگار باشند.
</div>