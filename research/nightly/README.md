# Nightly brain loop

- **Scheduled task:** "maniik nightly brain loop", ID `trig_01FXLbCpbXh2kKoD86SLvoew`. It was created 2026-11-02 with Manik's explicit approval.
- **Schedule:** daily at 22:37 IST (`CRON_TZ=Asia/Kolkata 37 22 * * *`). Each run starts a fresh cloud session and sends a push notification when it finishes.
- **Every night:** it runs all skill tests, grader selftest, routing and brain validate. It also adds missing eval cases for any new locks committed to main.
- **Sundays, additionally:** an official-source research refresh, plus small model evals (2 trials, 2 workers) only for the skills that changed that week.
- **Output:** `research/nightly/YYYY-MM-DD.md`, committed on a `claude/nightly-<date>` branch with a **draft PR**. Manik merges; the loop never pushes to main.
- **Coexistence:** it does not replace or duplicate the older ChatGPT 23:00 IST automation. That one reviews ChatGPT chats; this one works on the repo.
- **Manage:** at claude.ai/code/routines (pause, edit or delete).
