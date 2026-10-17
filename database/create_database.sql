-- Moodify: one-time PostgreSQL setup (no Docker needed).
-- Run as the PostgreSQL superuser, e.g.:
--   psql -U postgres -f database/create_database.sql
--
-- CREATEDB is required so `python manage.py test` can create a temporary test database.
-- Change the password for anything other than local development, and keep it in backend/.env.

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'moodify') THEN
      CREATE ROLE moodify WITH LOGIN PASSWORD 'moodify' CREATEDB;
   END IF;
END
$$;

SELECT 'CREATE DATABASE moodify OWNER moodify'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'moodify')\gexec
