# Database (PostgreSQL, no Docker)

Moodify uses a locally installed PostgreSQL (version 14 or newer; 16 recommended).
Django owns the schema through migrations, so you only create an empty database and user once.

## 1. Install PostgreSQL

- **Windows:** download the installer from https://www.postgresql.org/download/windows/ .
  Remember the password you set for the `postgres` user. Keep the default port 5432.
  `psql` lives in `C:\Program Files\PostgreSQL\16\bin` (add it to PATH or use the full path).
- **macOS:** `brew install postgresql@16 && brew services start postgresql@16`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install -y postgresql postgresql-contrib && sudo systemctl start postgresql`

## 2. Create the database and user

From the project root:

```bash
# Windows / macOS (superuser is "postgres"; you will be asked for its password)
psql -U postgres -f database/create_database.sql

# Ubuntu/Debian (uses the OS "postgres" account)
sudo -u postgres psql -f database/create_database.sql
```

This creates the role `moodify` (password `moodify`, allowed to create test databases) and the database `moodify`.

Check it works:

```bash
psql "postgresql://moodify:moodify@127.0.0.1:5432/moodify" -c "select 1;"
```

## 3. Point Django at it

`backend/.env` (copied from `backend/.env.example`) already has the matching defaults:

```
DB_NAME=moodify
DB_USER=moodify
DB_PASSWORD=moodify
DB_HOST=127.0.0.1
DB_PORT=5432
```

Then `python manage.py migrate` creates all the tables.

## Reset the database

```bash
psql -U postgres -c "DROP DATABASE moodify;"
psql -U postgres -f database/create_database.sql
cd backend && python manage.py migrate && python manage.py seed_songs
```

For production, use a different strong password and never commit it.
