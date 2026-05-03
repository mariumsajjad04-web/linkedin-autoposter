# LinkedIn Auto Poster — Setup Guide

Posts to your LinkedIn automatically 3x/day at peak hours using Claude AI.

---

## Step 1: Create a LinkedIn Developer App (15 min, one-time)

1. Go to https://www.linkedin.com/developers/apps and click **Create App**
2. Fill in:
   - App name: anything (e.g. "My Autoposter")
   - LinkedIn Page: your personal profile page URL
   - App logo: any image
3. After creation, go to the **Auth** tab:
   - Copy your **Client ID** and **Client Secret** — save these
   - Under "Authorized redirect URLs", add: `http://localhost:8080/callback`
4. Go to the **Products** tab and request access to **"Share on LinkedIn"**
   - It gets approved instantly

---

## Step 2: Get Your OAuth Tokens (5 min, one-time)

Run this on your local machine (requires Python):

```bash
cd linkedin-autoposter
pip install requests
python setup_tokens.py
```

- It will open LinkedIn in your browser
- Click **Allow**
- Your terminal will show the tokens — **copy them all**

---

## Step 3: Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/linkedin-autoposter.git
git push -u origin main
```

---

## Step 4: Add Secrets to GitHub

In your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add each of these:

| Secret Name | Value |
|---|---|
| `GEMINI_API_KEY` | From aistudio.google.com (free, no card needed) |
| `LINKEDIN_CLIENT_ID` | From Step 1 |
| `LINKEDIN_CLIENT_SECRET` | From Step 1 |
| `LINKEDIN_ACCESS_TOKEN` | From Step 2 |
| `LINKEDIN_REFRESH_TOKEN` | From Step 2 |
| `LINKEDIN_NICHE` | e.g. `tech and software development` |
| `LINKEDIN_TOPICS` | e.g. `AI tools,career lessons,side projects,productivity` |

---

## Step 5: Test It

In your GitHub repo → **Actions** tab → **LinkedIn Auto Post** → **Run workflow**

Check your LinkedIn profile — a post should appear within a minute.

---

## Schedule

Posts automatically at (India time, Mon–Fri):
- **8:00 AM**
- **12:00 PM**
- **6:00 PM**

To change the schedule, edit `.github/workflows/post.yml` and adjust the cron times.

---

## Customizing Your Content

Edit `LINKEDIN_TOPICS` secret to match your niche:
- Comma-separated list of topics
- Claude picks one randomly each time and writes a post around it

Example topics for different niches:
- Tech: `AI tools,open source,system design,startup lessons,developer productivity`
- Business: `sales lessons,founder mistakes,building in public,client stories`
- Career: `job search tips,salary negotiation,resume advice,networking`

---

## Token Refresh

- Access tokens expire in **60 days** — but the code auto-refreshes using your refresh token
- Refresh tokens last **1 year** — after that, re-run `setup_tokens.py`
