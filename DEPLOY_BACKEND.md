# Deploy Python Backend - Email with Port 587

## Changes Made

✅ **Added detailed logging** for SMTP connection
✅ **Better error handling** for authentication failures
✅ **Port 587 with STARTTLS** (30 second timeout)
✅ **No fallbacks** - requires EMAIL_USER and EMAIL_PASS

## What You Must Do

### Step 1: Add Environment Variables to Vercel

1. Go to https://vercel.com/
2. Select **format-a-python-backend** project
3. Settings → Environment Variables
4. Add these:

```
Name: EMAIL_USER
Value: formatateam@gmail.com
Environments: ✓ Production ✓ Preview ✓ Development

Name: EMAIL_PASS
Value: qrcrrrlodnywmsyw
Environments: ✓ Production ✓ Preview ✓ Development
```

### Step 2: Redeploy

After adding environment variables:
1. Deployments tab
2. Latest deployment → ⋯ → Redeploy
3. Wait 2-3 minutes

### Step 3: Test

Go to https://format-a.vercel.app and download a document.

## Logs to Check

In Vercel → format-a-python-backend → Functions → `/api/email-generator`:

**Success:**
```
📧 Email config check:
   EMAIL_USER: SET
   EMAIL_PASS: SET
📧 Connecting to smtp.gmail.com:587...
📧 Starting TLS...
📧 Logging in as formatateam@gmail.com...
📧 Sending email to user@example.com...
✅ Email sent successfully to user@example.com
```

**Failure (no env vars):**
```
📧 Email config check:
   EMAIL_USER: NOT SET
   EMAIL_PASS: NOT SET
❌ EMAIL_USER and EMAIL_PASS must be set in Vercel environment variables
```

**Failure (auth error):**
```
❌ SMTP Authentication failed: ...
   Check EMAIL_USER and EMAIL_PASS are correct
```

## Summary

- Port 587 with STARTTLS
- 30 second timeout
- Detailed logging
- Clear error messages
- No fallbacks

Deploy and test!
