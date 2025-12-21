# Configuration Guide

## Required Environment Variables

### For Scoring Candidates (LLM)

To enable candidate scoring, you need to set:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Optional:
```bash
OPENAI_API_BASE=https://api.openai.com/v1  # Default
LLM_MODEL=gpt-4o-mini  # Default
```

**Note:** Without `OPENAI_API_KEY`, you can still use the application but candidates won't be scored automatically. You can view candidates and manually review them.

### For Sending Emails (SMTP)

To enable email sending (interview/rejection emails), configure SMTP settings:

```bash
SMTP_HOST=smtp.gmail.com  # Default
SMTP_PORT=587  # Default
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true  # Default
```

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password as `SMTP_PASSWORD`

**Note:** Without SMTP configuration, you can still use the application but won't be able to send emails to candidates.

## Setting Environment Variables

### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="your-key-here"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-password"
```

### Windows (Command Prompt)
```cmd
set OPENAI_API_KEY=your-key-here
set SMTP_USERNAME=your-email@gmail.com
set SMTP_PASSWORD=your-password
```

### Linux/Mac
```bash
export OPENAI_API_KEY="your-key-here"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-password"
```

### Using .env file

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your-openai-api-key-here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
```

The application will automatically load these variables.

## Testing Configuration

1. **Test Scoring:** Select a job and view candidates. If scoring works, you'll see scores. If not, you'll see an error message.

2. **Test Email:** Try sending an interview or rejection email. If SMTP is configured, emails will send. If not, you'll see a helpful error message.

## Troubleshooting

### Scoring Not Working
- Error: "Scoring service is not configured"
- Solution: Set `OPENAI_API_KEY` environment variable

### Email Not Sending
- Error: "SMTP authentication failed"
- Solution: Check `SMTP_USERNAME` and `SMTP_PASSWORD`
- For Gmail: Use App Password, not regular password

- Error: "Could not connect to SMTP server"
- Solution: Check `SMTP_HOST` and `SMTP_PORT`





