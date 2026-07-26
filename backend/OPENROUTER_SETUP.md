# OpenRouter API Setup Guide

## Environment Variables

To use OpenRouter instead of OpenAI, set these environment variables:

```bash
# Required
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-api-key-here
LLM_MODEL=openai/gpt-4o-mini

# Optional (has defaults)
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1  # Default value
```

## Important Notes

### 1. Model Name Format
OpenRouter requires model names with provider prefix:
- ✅ `openai/gpt-4o-mini`
- ✅ `openai/gpt-4o`
- ✅ `anthropic/claude-3-haiku`
- ✅ `google/gemini-pro`
- ❌ `gpt-4o-mini` (missing provider prefix)

### 2. API Key
- You can use either `OPENROUTER_API_KEY` or `OPENAI_API_KEY` (for compatibility)
- Get your key from: https://openrouter.ai/keys

### 3. Base URL
- Default: `https://openrouter.ai/api/v1`
- Only set `OPENROUTER_BASE_URL` if you need a custom endpoint

## Example .env File

```env
# OpenRouter Configuration
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
LLM_MODEL=openai/gpt-4o-mini

# Optional headers (for analytics)
HTTP_REFERER=http://localhost:8000
APP_TITLE=RecroAI
```

## Common Issues

### Issue: "LLM_MODEL must be set"
**Solution:** Set `LLM_MODEL` environment variable with provider prefix:
```bash
LLM_MODEL=openai/gpt-4o-mini
```

### Issue: "OPENROUTER_API_KEY must be set"
**Solution:** Set `OPENROUTER_API_KEY` or use `OPENAI_API_KEY`:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
```

### Issue: Model not found / 404 error
**Solution:** Check model name format. Must include provider prefix:
- Wrong: `gpt-4o-mini`
- Correct: `openai/gpt-4o-mini`

### Issue: JSON parsing errors
**Solution:** The code automatically handles markdown code blocks from OpenRouter responses. If you still see errors, check that the model supports JSON mode.

## Testing

Test your OpenRouter setup:
```bash
cd backend
python test_openrouter.py
```

This will verify:
- API key is set correctly
- Model name is valid
- Base URL is accessible
- JSON responses are parsed correctly

