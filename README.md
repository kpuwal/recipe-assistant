# Recipe Assistant

Chat-based recipe companion built with a React Native mobile frontend and a FastAPI backend.

## Stack

- **Mobile**: Expo 54 · React Native 0.81 · React 19
- **Backend**: FastAPI · Python 3.12 · Uvicorn
- **Integrations**: Groq (AI), Dropbox, Google Cloud Storage, PyMuPDF

## What it does

- Search and manage recipes via a chat interface
- Filter recipes by tags (e.g. "ontbijt", "diner")
- View, add, edit, and delete recipes
- Sync recipes from external sources (Dropbox / GCS)
- AI-generated recipe suggestions

## Project structure

```
apps/
  backend/     # FastAPI API server
  mobile/      # Expo React Native app
```

## Getting started

### Backend
```
cd apps/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Mobile
```
cd apps/mobile
npm install
npx expo start
```

## Deploy

Backend is containerised with Docker and deployed to Google Cloud Run.  
Mobile builds are published via `eas build --platform android --profile preview`.
