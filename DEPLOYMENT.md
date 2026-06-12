# 🚀 BLACKOUT Production Deployment Manual

Follow this pipeline to deploy your game bot to Telegram and host it 24/7.

---

## Phase 1: BotFather Registration

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Choose a display name (e.g., "BLACKOUT Bot")
4. Choose a username ending in `_bot` (e.g., "BLACKOUT_Game_bot")
5. **Save the API token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Group Settings

1. Send `/setprivacy` to BotFather
2. Select your bot
3. Set to **DISABLED** (allows bot to read all messages)
4. Send `/setjoingroups`
5. Ensure it's **ENABLED**

---

## Phase 2: Local Testing

1. Navigate to your project:
```bash
cd blackout-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your token:
```bash
# Linux/macOS
export TELEGRAM_BOT_TOKEN="your_token_here"

# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="your_token_here"
```

4. Run the bot:
```bash
python bot.py
```

5. Test in Telegram:
   - Create a test group
   - Add your bot
   - Send `/join`
   - Send `/add_bots`
   - Send `/start_game`

---

## Phase 3: Cloud Deployment (Railway)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "feat: blackout bot v1.0"
git remote add origin https://github.com/YOUR_USERNAME/blackout-bot.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your `blackout-bot` repository

### Step 3: Configure Environment

1. Go to your service's **Variables** tab
2. Add:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `DATABASE_PATH` = `blackout.db` (optional, default works)

### Step 4: Deploy

Railway auto-detects Python and runs `bot.py`.

---

## Phase 4: Monitoring

### Logs
- Check Railway deployment logs for errors
- Monitor bot responsiveness

### Database
- SQLite file `blackout.db` stores all game data
- Back up periodically

### Scaling
- For high traffic, migrate to PostgreSQL
- Consider Redis for session management

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot doesn't respond | Check token, ensure privacy is disabled |
| Can't add to group | Ensure `/setjoingroups` is enabled |
| DMs fail | Users must start a PM with bot first |
| Game doesn't start | Need minimum 4 players |
| Database errors | Check file permissions, restart bot |

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `/join` | Join the lobby |
| `/leave` | Leave the lobby |
| `/add_bots` | Fill to 10 with AI players |
| `/start_game` | Start immediately |
| `/corrupt_count 1` | Set 1 corrupt (creator only) |
| `/corrupt_count 2` | Set 2 corrupt (creator only) |
| `/help` | Show game rules |
| `/players` | Show lobby players |
| `/vote @username` | Vote during day phase |
| `/skip` | Skip vote |
| `/spectate` | View as dead player |
| `/stats` | Your ELO and record |
| `/leaderboard` | Top players |
