# One-time setup (about 15 minutes) — then everything posts by itself

Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add these:

## 1. META_PAGE_TOKEN (Facebook Page + Instagram + stories)
1. developers.facebook.com → My Apps → **Create app** → "Other" → **Business** → name `NFP Publisher` → connect your business portfolio.
2. In the app add the use cases **Manage everything on your Page** and **Instagram API (Facebook login)**.
3. Tools → **Graph API Explorer** → choose the app → *Get User Access Token* with: `pages_show_list, pages_read_engagement, pages_manage_posts, business_management, instagram_basic, instagram_content_publish` → allow for **Noida Farmhouse Party** and **@noidafarmhouseparty**.
4. Click the ⓘ next to the token → **Open in Access Token Tool** → **Extend Access Token** → copy the long-lived token.
5. Back in Graph API Explorer paste it, run `GET me/accounts`, copy the `access_token` shown for *Noida Farmhouse Party* → save as **META_PAGE_TOKEN** (this Page token does not expire).

## 2. THREADS_TOKEN
1. Same app → add use case **Access the Threads API** → permissions `threads_basic, threads_content_publish`.
2. App roles → add **noidafarmhouseparty** as Threads tester → accept it in Threads (Settings → Account → Website permissions → Invites).
3. Threads use case → **Generate access token** (long-lived) → save as **THREADS_TOKEN**. The workflow refreshes it every week by itself.

## 3. YouTube (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN)
1. console.cloud.google.com (as noidafarmhouseparty@gmail.com) → new project `nfp-publisher` → enable **YouTube Data API v3**.
2. **OAuth consent screen** → External → app name + email → add scopes `.../auth/youtube.upload` and `.../auth/youtube` → **Publish app** (unverified is fine for your own channel; this stops the token expiring after 7 days).
3. **Credentials → Create OAuth client ID → Web application** → redirect URI `https://developers.google.com/oauthplayground` → copy Client ID and Secret → save as **YT_CLIENT_ID**, **YT_CLIENT_SECRET**.
4. developers.google.com/oauthplayground → ⚙ → *Use your own OAuth credentials* → paste both → in "Input your own scopes" type `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube` → **Authorize APIs** (pick the Noida Farmhouse Party channel; on the unverified screen use Advanced → Continue) → **Exchange authorization code for tokens** → copy the **Refresh token** → save as **YT_REFRESH_TOKEN**.
5. Optional: verify the channel phone at youtube.com/verify so custom thumbnails work.

## 4. Test
Actions → **publish** → Run workflow → task `check` → it must print `META OK`, `THREADS OK`, `YOUTUBE OK` and `MEDIA 200`.
