# Frontend - Enterprise Knowledge Assistant

Next.js 14 App Router frontend with TypeScript, Tailwind CSS, React Query, and Zustand.

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Ensure NEXT_PUBLIC_API_BASE=http://localhost:8000

# 2. Install dependencies
pnpm install  # or npm install

# 3. Run dev server
pnpm dev
```

Open http://localhost:3000

## Structure

- `app/` - Next.js App Router pages (layout, chat, ingest, search)
- `components/` - React components (chat, UI primitives, metrics, sources)
- `lib/` - Client hooks, validators (Zod), store (Zustand)
- `styles/` - Global Tailwind styles

## Pages

- `/` - Chat UI with message list, composer, metrics, sources panel
- `/ingest` - Ingest page for building index from file paths
- `/search` - Semantic search interface

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (`@tanstack/react-query`)
- Zustand
- React Markdown + Highlight.js
- Minimal shadcn/ui-style primitives

## Environment Variables

- `NEXT_PUBLIC_API_BASE` - Backend API URL (default: http://localhost:8000)

## Build

```bash
pnpm build
pnpm start
```

## Testing

```bash
pnpm test
```

