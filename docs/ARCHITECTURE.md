# Architecture

## Request flow

React/Vite → Axios → Django REST Framework → PostgreSQL

Authentication is handled by Django Simple JWT. The frontend stores access/refresh tokens locally and automatically refreshes an expired access token.

## Backend responsibilities

`api/views.py`
- HTTP endpoints
- authentication and authorization
- query filtering
- persistence orchestration

`api/serializers.py`
- request validation
- response shaping

`api/mood_analyzer.py`
- deterministic local mood/emotion/energy classification

`api/recommendation_engine.py`
- deterministic ranking from mood, energy, profile preferences, history and popularity

`api/models.py`
- PostgreSQL schema represented by Django ORM

## Frontend responsibilities

`context/`
- authentication, theme, player, notifications

`services/`
- one API boundary for all server operations

`pages/`
- route-level UI

`components/`
- reusable visual and player primitives

The frontend does not contain database credentials and does not make database calls.
