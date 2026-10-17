# Development notes

## Before committing

Run:

```bash
cd backend
python manage.py check
python manage.py test

cd ../frontend
npm run lint
npm run build
```

## Database changes

Change `backend/api/models.py`, then create a migration with:

```bash
python manage.py makemigrations
python manage.py migrate
```

Never edit an already-applied production migration to change historical schema.

## UI direction

The interface uses a restrained editorial visual system:
- warm neutral surfaces
- strong typography
- one green accent
- thin borders
- minimal shadows
- no glassmorphism
- no excessive gradients
- clear information hierarchy

This is intentional: the product should feel like a considered music tool rather than a generic AI dashboard.
