# Phase 1 Architecture

## Backend

### Core Layers

- `app/core/` settings, security, dependencies, errors
- `app/db/` engine, session, metadata creation
- `app/models/` SQLAlchemy entities
- `app/schemas/` request and response models
- `app/services/` business logic
- `app/api/routes/` HTTP routers

### Models

- `User`
- `Patient`
- `Doctor`
- `Appointment`

### Key Workflows

- Register and login users with JWT
- Create/update/delete/search patients
- Create/update/delete/search doctors
- Book, reschedule, approve, and cancel appointments
- Prevent conflicting doctor slot bookings

## Frontend

### Key Layers

- `src/api/` Axios API clients
- `src/context/` authentication state
- `src/components/` shared layout and UI primitives
- `src/pages/` auth, dashboards, and management screens

### Routes

- `/login`
- `/register`
- `/dashboard/admin`
- `/dashboard/doctor`
- `/dashboard/patient`
- `/patients`
- `/doctors`
- `/appointments`

