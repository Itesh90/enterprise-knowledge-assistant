# Gemini API Setup Guide

## Issues You're Experiencing

1. **API Key Not Found**: The error "Provide a Gemini API key to enable generation" means the API key is not being read from your `.env` file.
2. **Model Name**: "gemini 2.5 flash" is not a valid model name. Use one of these:
   - `gemini-1.5-flash` (recommended - fast and cheap)
   - `gemini-1.5-pro` (more capable, slower)
   - `gemini-2.0-flash-exp` (experimental, very fast)

## Step-by-Step Fix

### 1. Create/Update `.env` File

Create a file named `.env` in the `backend/` folder with this content:

```env
GEMINI_API_KEY=your-api-key-here
LLM_MODEL=gemini-1.5-flash
```

**Replace `your-api-key-here` with your actual Gemini API key from Google AI Studio.**

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key" in the left sidebar
3. Create a new project or select existing one
4. Copy the API key
5. Paste it in your `.env` file

### 3. Verify Model Name

Make sure your `.env` file has one of these valid model names:
- `LLM_MODEL=gemini-1.5-flash` (recommended)
- `LLM_MODEL=gemini-1.5-pro`
- `LLM_MODEL=gemini-2.0-flash-exp`

### 4. Restart the Backend

After updating the `.env` file, **restart your backend server** for changes to take effect:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
python -m uvicorn app.api.main:app --reload --port 8000
```

Or if using `npm run dev` from root, restart that command.

## File Location

Your `.env` file should be at:
```
enterprise-knowledge-assistant/backend/.env
```

## Example `.env` File

```env
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
ENABLE_RERANKER=false
CITATION_SIM_THRESHOLD=0.30
```

## Troubleshooting

- **Still getting API key error?** Make sure:
  - The `.env` file is in `backend/` folder (not root)
  - The key is exactly `GEMINI_API_KEY=your-key` (no quotes, no spaces around `=`)
  - You restarted the backend server after adding the key
  
- **Model name error?** Check that you're using one of the valid names listed above (with hyphens, not spaces).

