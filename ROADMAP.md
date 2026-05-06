# Multi-Platform Autoposter — Roadmap

This is your post-exams expansion plan. Open this file when you're ready, follow the phases in order. Each phase builds on the previous.

---

## ✅ Phase 1 — DONE (Current State)

- [x] LinkedIn AI post generator (Python + Gemini)
- [x] GitHub Actions scheduler (3x/day, weekdays)
- [x] Email delivery with auto-generated quote card image
- [x] 4 post frameworks (build story, hot take, free value, lesson)
- [x] Personal context baked into AI prompts
- [x] Retry logic with model fallbacks
- [x] Traffic-driving CTAs

**Status:** Production. You receive 3 posts/day with images, copy-paste to LinkedIn.

---

## 🟢 Phase 2 — Instagram (separate portfolio account)

**Why separate account:** Algorithm punishes mixed-niche accounts. Fresh start = clean signal.

### Step 1: Create accounts (15 min)
- [ ] New Instagram account: `@marium.builds` (or whatever handle is free)
- [ ] Switch to **Creator** or **Business** account in settings (required for API)
- [ ] Bio: same hook as LinkedIn headline
- [ ] Profile photo: same as LinkedIn
- [ ] Add link to Archlane + GitHub

### Step 2: Connect Instagram → Facebook (required by Meta)
- [ ] Create a new Facebook Page (NOT personal profile) — name: same as Insta
- [ ] In Insta app: Settings → Account Center → Add Facebook account
- [ ] Link the Page to Insta business profile

### Step 3: Set up Meta Developer App (30 min)
- [ ] Go to: https://developers.facebook.com/apps
- [ ] Create App → Type: "Business" → Name: "Marium Autoposter"
- [ ] Add product: **Instagram Graph API**
- [ ] Add product: **Facebook Login**
- [ ] Configure OAuth redirect: `http://localhost:8080/callback`

### Step 4: Get long-lived access token (15 min)
- [ ] Use Graph API Explorer to get short-lived token with these permissions:
  - `instagram_basic`
  - `instagram_content_publish`
  - `pages_show_list`
  - `pages_read_engagement`
- [ ] Exchange for long-lived token (60 days, refreshable)
- [ ] Save these as GitHub Secrets:
  - `META_APP_ID`
  - `META_APP_SECRET`
  - `META_LONG_LIVED_TOKEN`
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`
  - `FACEBOOK_PAGE_ID`

### Step 5: Image hosting (Instagram requires public URL)
**Option A — Imgur (free, simple):**
- [ ] Register app at https://api.imgur.com/oauth2/addclient
- [ ] Get `IMGUR_CLIENT_ID` (no auth needed for anonymous uploads)

**Option B — Cloudinary (free tier 25GB):**
- [ ] Sign up at cloudinary.com
- [ ] Get cloud name + API key + secret

### Step 6: Code changes
Add `instagram_poster.py`:
```python
import os, requests

def upload_image_to_imgur(image_path):
    with open(image_path, "rb") as f:
        resp = requests.post(
            "https://api.imgur.com/3/image",
            headers={"Authorization": f"Client-ID {os.environ['IMGUR_CLIENT_ID']}"},
            files={"image": f},
        )
    resp.raise_for_status()
    return resp.json()["data"]["link"]

def post_to_instagram(image_url, caption):
    ig_id = os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    token = os.environ["META_LONG_LIVED_TOKEN"]
    
    # Step 1: Create container
    create = requests.post(
        f"https://graph.facebook.com/v18.0/{ig_id}/media",
        params={"image_url": image_url, "caption": caption, "access_token": token},
    )
    container_id = create.json()["id"]
    
    # Step 2: Publish
    publish = requests.post(
        f"https://graph.facebook.com/v18.0/{ig_id}/media_publish",
        params={"creation_id": container_id, "access_token": token},
    )
    return publish.json()
```

### Step 7: Update workflow
Add new env vars to `.github/workflows/post.yml` and modify `main.py` to call `post_to_instagram()` after image generation.

### Step 8: Token refresh automation
Meta tokens expire every 60 days. Add a separate workflow that runs monthly to refresh:
```yaml
# .github/workflows/refresh-meta-token.yml
on:
  schedule:
    - cron: '0 0 1 * *'  # First day of every month
```

**Estimated total time:** 2-3 hours for first-time setup

---

## 🟡 Phase 3 — Facebook Page (basically free with Phase 2)

Once Phase 2 works, Facebook Page posting uses the SAME API. ~30 minutes to add.

### Step 1: Add to existing code
```python
def post_to_facebook(image_url, caption):
    page_id = os.environ["FACEBOOK_PAGE_ID"]
    token = os.environ["META_LONG_LIVED_TOKEN"]
    resp = requests.post(
        f"https://graph.facebook.com/v18.0/{page_id}/photos",
        params={"url": image_url, "caption": caption, "access_token": token},
    )
    return resp.json()
```

### Step 2: Call after Instagram in main.py
That's it. Same token, same image.

---

## 🟢 Phase 4 — Threads (Meta's Twitter clone)

Meta released Threads API in mid-2024. Same Graph API approach.

- [ ] Add `threads_basic` and `threads_content_publish` permissions to existing Meta app
- [ ] Get `THREADS_USER_ID` (different from Instagram ID)
- [ ] Add `post_to_threads()` function (similar pattern to Instagram)

**Estimated time:** 1 hour after Phase 2

---

## 🟡 Phase 5 — Revisit LinkedIn API (optional)

Skip the email step entirely. Direct posting to LinkedIn.

### Known blockers from previous attempt:
- LinkedIn API version mismatches (we tried 202304, 202408, 202504 — none worked)
- `urn:li:person:` vs `urn:li:member:` URN format conflict
- 403 ACCESS_DENIED on author field

### Approach for retry:
- [ ] Use LinkedIn's NEW community-managed API (Posts API, not UGC Posts)
- [ ] Test in LinkedIn API console FIRST before coding
- [ ] Verify token scope includes `w_member_social` AND `r_liteprofile`
- [ ] Use `/v2/userinfo` endpoint to fetch member ID at runtime (don't trust stored PERSON_ID)

**Estimated time:** 4-8 hours of debugging (LinkedIn API is famously bad)

**Honest take:** Email approach works fine. Manual copy-paste = 10 seconds. Direct API = hours of debugging. Only do this if you're posting 10+ times/day.

---

## 🔴 Phase 6 — YouTube (skip unless making real videos)

YouTube requires actual video files. Auto-generated slideshow videos look cheap.

**Only do this if:**
- You start recording real screen-recording tutorials
- You want to repurpose tutorial videos as Shorts

**If pursuing:**
- Use YouTube Data API v3
- Quota: 10,000 units/day, video upload = 1,600 units (~6/day)
- Need OAuth flow + refresh tokens

---

## 🟢 Phase 7 — Personal Portfolio Website

Inspiration: https://designifyhub.netlify.app/

### Stack (use what you already know):
- Next.js (frontend)
- Supabase (contact form submissions)
- Resend (email notifications when someone DMs)
- Vercel (free hosting)
- Domain: `marium.dev` or `mariumbuilds.com` (~$12/year)

### Sections (Designify-style):
1. **Hero:** Outcome-focused headline + CTA
2. **Services:** Web, Backend, Automation, AI integration (with starting prices)
3. **Case studies:** Archlane Properties + LinkedIn Bot + 1-2 more
4. **About:** Short bio with personal photo
5. **Process:** How working with you actually works (3 steps)
6. **Contact:** Form → Resend → your email + WhatsApp link

### Time estimate:
- Design: 1 weekend (use a Figma template + customize)
- Build: 2-3 weekends (you already know the stack)
- Polish + launch: 1 weekend

**Total:** 4 weekends to a real client-converting portfolio.

---

## 🟢 Phase 8 — SEO + Discoverability

Once portfolio is live:
- [ ] Submit to Google Search Console
- [ ] Add to Pakistan freelancer directories
- [ ] List on LinkedIn ProFinder
- [ ] Create Upwork profile (link to portfolio)
- [ ] Write blog posts about each project (Hashnode is free + SEO-friendly)

---

## 📊 Success Metrics

Track these monthly:

| Metric | Phase 1 (now) | After Phase 4 | After Phase 7 |
|--------|---------------|---------------|---------------|
| Posts/week | 15 (LinkedIn only) | 60 (4 platforms) | Same + portfolio |
| Followers gained/month | ? | Track | Track |
| DMs received/month | ? | Track | Track |
| Client inquiries/month | 0 | Track | Track |
| Real projects landed | 0 | Track | Goal: 1-2 |

---

## 🌙 Final note

You shipped a working product in 24 hours. Most devs ship nothing.

Don't burn out trying to do all phases at once. Order matters:
1. Finish exams 📚
2. Phase 2-3 (Instagram + Facebook) — 1 weekend
3. Phase 7 (portfolio site) — 4 weekends
4. Phase 4 (Threads) — 1 evening
5. Skip Phase 5 unless you really want it
6. Skip Phase 6 unless you're recording videos

By the time you finish Phase 7, you'll have a real freelance business setup. From a student in Karachi, that's not a small thing.

— Built with ❤️ during a 24-hour debug session 🐛
