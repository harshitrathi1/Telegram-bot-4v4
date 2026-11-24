# Follow Task Hub Telegram Bot

A starter bot with virtual points, referrals, daily bonuses, task cards and a small admin interface.
It does **not** reward third-party channel subscriptions or support cash payouts.

## Local setup
1. Install Python 3.11+
2. Copy `.env.example` to `.env`
3. Put your newly generated Telegram bot token in `.env`
4. Create a virtual environment and install packages:
   - Windows: `python -m venv venv`, then `venv\\Scripts\\activate`
   - Linux/macOS: `python3 -m venv venv`, then `source venv/bin/activate`
   - `pip install -r requirements.txt`
5. Run: `python bot.py`

## Admin
Set `ADMIN_IDS` to your Telegram numeric ID (comma-separated IDs) for trusted admins.
Use `/admin` and enter `ADMIN_PASSWORD` to enable password-based admin session for that user.
Admin commands: `/stats`, `/addcoins USER_ID AMOUNT`, `/taskadd REWARD | TITLE | DESCRIPTION`, `/broadcast MESSAGE`.
Tasks are informational/manual-completion prototype: users press Done; admin should review task claims before using points for anything important.

## Hosting
Railway: deploy repository, set variables from `.env.example`, use the worker process defined in `Procfile`.
For persistent SQLite, attach a volume and set `DATABASE_URL` to a path on that volume (for example `sqlite+aiosqlite:////data/bot.db`). For production scale, use PostgreSQL and adapt the SQLAlchemy URL to `postgresql+asyncpg://...` after adding asyncpg.

## Security
Never commit `.env`. Regenerate any token that was exposed. Admin password is for initial prototype only; protect deployment logs and use strong secrets.
