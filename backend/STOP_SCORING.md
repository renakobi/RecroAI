# How to Stop Stuck Scoring Process

## Immediate Stop

If scoring is stuck and spending tokens:

1. **Press Ctrl+C** in the terminal where uvicorn is running
2. If that doesn't work, close the terminal window
3. If still stuck, use Task Manager:
   - Press `Ctrl+Shift+Esc`
   - Find `python.exe` or `uvicorn` processes
   - Right-click → End Task

## Prevention

- Maximum 50 candidates can be scored at once (safety limit)
- Each candidate takes 5-15 seconds to score (LLM calls are slow)
- 17 candidates = ~2-5 minutes total
- If it's taking longer, something is wrong - stop it!

## Check Token Usage

After stopping, check your OpenRouter dashboard to see how many tokens were used.

## Restart Safely

After stopping:
1. Wait 10 seconds
2. Restart server: `uvicorn app.main:app --reload`
3. Try scoring with fewer candidates first (1-2) to test

