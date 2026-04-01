# East / West Review — Automated Newsletter

Weekly newsletter covering cultural life in Oakland & San Francisco. Delivered every Sunday morning via GitHub Actions + Anthropic API + Resend.

## Setup

### 1. Add repository secrets

In your GitHub repo → Settings → Secrets and variables → Actions, add these four secrets:

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (from console.anthropic.com) |
| `RESEND_API_KEY` | Your Resend API key (from resend.com/api-keys) |
| `RECIPIENT_EMAIL` | Your email address |
| `FROM_EMAIL` | The sender address, e.g. `East / West Review <newsletter@yourdomain.com>` |

### 2. Verify your sending domain in Resend

In your Resend dashboard, add and verify the domain you're sending from. The `FROM_EMAIL` address must match a verified domain.

If you don't have a custom domain, Resend provides a default `onboarding@resend.dev` address for testing — use that as `FROM_EMAIL` while setting up.

### 3. Enable GitHub Actions

Make sure Actions are enabled in your repo (Settings → Actions → General → Allow all actions).

### 4. Test it

Go to Actions → "East / West Review — Sunday delivery" → Run workflow to trigger a manual send and confirm everything works before the first scheduled run.

## Schedule

Runs every Sunday at 14:00 UTC (6:00 AM Pacific Standard Time).

**Note on Daylight Saving Time:** During PDT (mid-March to early November), 14:00 UTC = 7:00 AM Pacific. To keep it at 6:00 AM year-round, change the cron in `.github/workflows/newsletter.yml`:
- Standard time (Nov–Mar): `0 14 * * 0`
- Daylight saving (Mar–Nov): `0 13 * * 0`

## Files

```
├── generate_newsletter.py     # Calls Anthropic API to research and write the issue
├── send_newsletter.py         # Sends the HTML via Resend
├── .github/
│   └── workflows/
│       └── newsletter.yml     # GitHub Actions schedule and workflow
└── README.md
```

## How it works

1. Every Sunday at 6am, GitHub Actions wakes up and runs the workflow
2. `generate_newsletter.py` calls Claude (claude-opus-4-6) with the full newsletter brief and a web search tool
3. Claude researches real events across all sources, applies editorial judgment, and returns complete HTML
4. `send_newsletter.py` passes that HTML to Resend, which delivers it to your inbox
5. The generated HTML is also saved as a GitHub Actions artifact for 90 days (useful for reference)

## Manual trigger

You can trigger a send at any time from GitHub Actions → "East / West Review — Sunday delivery" → Run workflow.
