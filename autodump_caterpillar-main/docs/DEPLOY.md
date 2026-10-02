# Deploy Agentic AI-Based Dump Site Optimization to GitHub Pages

You have everything you need. Pick **one** of the two paths below.

| Path | Time | Best when |
|---|---|---|
| **A. Web upload (drag-and-drop)** | ~3 min | You want it live ASAP, no terminal |
| **B. Git command line** | ~5 min | You'll iterate on the site later |

Repository: <https://github.com/Krishnapriya-007/Optimal-Dump-Packing>

---

## ⚡ Path A — Web upload (no terminal)

1. **Create the repository.** Go to <https://github.com/new>
      - **Repository name**: `Optimal-Dump-Packing`
   - **Public** (required for free GitHub Pages)
   - ✓ "Add a README file" — leave checked, we'll overwrite it
   - Click **Create repository**

2. **Upload the files.** On your new repo page, click **"Add file → Upload files"**.
       - Drag the entire contents of this `site/` folder into the browser
             (the `index.html`, `404.html`, `.nojekyll`, and `CNAME.example` files)
   - **Important:** the `.nojekyll` file is invisible on macOS Finder.
     Show hidden files: `Cmd + Shift + .` On Windows: View → Show → Hidden items.
   - At the bottom: **Commit changes**

3. **Enable Pages.** On your repo: **Settings → Pages**.
   - **Source**: select **"Deploy from a branch"**
   - **Branch**: `main`, folder `/ (root)`
   - **Save**

4. **Wait 30-60 seconds**, then refresh the Pages settings.
      GitHub will show the published Pages URL in the repository settings.

5. **Open it.** Click that URL. Done.

---

## 🛠 Path B — Git command line

```bash
# 1. Make the repo locally
mkdir Optimal-Dump-Packing && cd Optimal-Dump-Packing
# Drag the contents of the deploy/ folder into here, then:
git init
git add .
git commit -m "Initial deploy: Agentic AI dump-site dashboard"
git branch -M main

# 2. Create the empty repo on GitHub
#    Go to https://github.com/new
#    Name: Optimal-Dump-Packing
#    Visibility: Public
#    Do NOT add a README on the GitHub side (we already have one)
#    Click "Create repository"

# 3. Push to the configured project repository
git remote add origin https://github.com/Krishnapriya-007/Optimal-Dump-Packing.git
git push -u origin main

# 4. Enable Pages
#    Repo → Settings → Pages → Source = "GitHub Actions"
#    (Or "Deploy from branch" → main → /, both work.)
#
# 5. Wait ~30s. Open the GitHub Pages URL shown in repository settings.
```

---

## ✅ Post-deploy checklist (5 minutes)

After the URL is live, use this checklist to verify the project site.

- [ ] **Open the live URL on your laptop in a private/incognito window.**
      All 8 pages load. The trained agent reaches ~75% coverage on Live RL Simulation.
- [ ] **Open it on your phone.** The dashboard is desktop-first but should be readable.
      If you'll demo from a phone, switch the phone to landscape.
- [ ] **Test airplane mode.** Disconnect WiFi. Hit refresh. Everything should still work
      (only Google Fonts is missing; the layout uses system font fallbacks).
- [ ] **Test the Custom Field page.** Click ▭ Rectangle → ✓ Close + run.
      Should show 2 zones, ~99.9% greedy coverage.
- [ ] **Test the Token Protocol page.** Click each of the 4 scenarios.
      Confirm CLEARANCE appears in the Crash scenario.
- [ ] **Share the URL in a chat (Slack/WhatsApp/LinkedIn).** Confirm the preview card
      shows the Agentic AI project title + description (Open Graph tags). If it shows just
      "github.io", clear the platform's link cache and try again.
- [ ] **Check the project links.** Confirm README and Open Graph links point to this repository.

---

## Optional custom domain

Skip this if you're happy with `*.github.io`. Otherwise:

1. **Buy a domain.** Namecheap, Porkbun, or Cloudflare Registrar (~₹700/year for `.com`).
2. In your domain registrar, add a **CNAME** record:
   - Host: `@` (or `www`)
      - Value: `Krishnapriya-007.github.io`
3. In `site/`, rename `CNAME.example` → `CNAME` and put your domain on the first line:
   ```
      project.example
   ```
4. Commit, push. GitHub will detect it and provision HTTPS automatically (takes 1-15 min).
5. Update the `<link rel="canonical">` and OG `og:url` meta tags in `site/index.html` to your
   new domain.

---

## 🔁 Updating the site after launch

Just push a new `site/index.html` and the site updates within ~30 seconds.

```bash
# Make changes to site/index.html, then:
git add site/index.html
git commit -m "Update: <what you changed>"
git push
```

If you set up the optional GitHub Actions workflow (in `.github/workflows/pages.yml`),
Pages will deploy automatically. Otherwise it deploys directly from `main`.

---

## 🐛 Troubleshooting

| Symptom | Fix |
|---|---|
| **"404 Not Found" on the live URL** | Pages may still be building. Wait 60s and refresh. If still failing after 5 min: Settings → Pages → confirm source is set correctly. |
| **Site loads, but fonts differ** | The browser blocked Google Fonts. The fallback system fonts will render — layout still works. |
| **Token timeline looks empty** | The 0-second event is at left edge. Hover the dots to see tooltips with t/kind/note. |
| **Custom Field "click to start" stays after I click** | Browser zoom != 100%. Hit Ctrl/Cmd+0. |
| **Q-agent only reaches 30%** | You re-loaded a non-original polygon. Hit "⟲ Default polygon" on the Custom Field page. |
| **Pages shows old version after I pushed** | Cloudflare/browser cache. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R). Or wait ~60s for GitHub's CDN. |

---

## 📊 Add analytics (optional, no PII)

GitHub Pages doesn't ship analytics. If you want a per-visit counter:

- **Plausible Analytics** — privacy-friendly, paid (~$9/mo). Add one line in `<head>`.
- **GoatCounter** — free, no cookies. Add one `<script>` tag in `<head>`.
- **Vercel Web Analytics** if you ever migrate from Pages — free, automatic.

Skip this for the competition. Add it after the finale if you want post-event stats.

---

## 🎯 You're done.

Open the published URL and verify the site pages and planning workflow.

Department of Computer Science · 2026
