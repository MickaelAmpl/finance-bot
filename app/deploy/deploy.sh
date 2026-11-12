#!/usr/bin/env bash
# Deploy the finance bot from this Mac to the server (systemd units in /opt/finance-bot).
#
#   FINBOT_HOST=myvps app/deploy/deploy.sh --dry-run   # print every step, change nothing
#   FINBOT_HOST=myvps app/deploy/deploy.sh             # deploy
#
# Refuses to run with uncommitted changes under app/. The server's .env is checked for the
# BOT_TOKEN and OWNER_ID keys and mode 600 only; step 5 also reports whether ANTHROPIC_API_KEY
# is present or missing. Its values are never printed.

set -Eeuo pipefail

HOST="${FINBOT_HOST:-myvps}"
APP=/opt/finance-bot
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP="/opt/finance-bot-backups/$(date +%Y-%m-%d-%H%M%S)"
HAS_BACKUP=0
DB_TOUCHED=0

# Restores the database copy only. test -f comes first, so nothing is removed without the backup.
rollback_line() {
  echo "ssh $HOST \"test -f '$BACKUP/finbot.db' && systemctl stop finance-bot.service && rm -f '$APP/data/finbot.db-wal' '$APP/data/finbot.db-shm' && cp '$BACKUP/finbot.db' '$APP/data/finbot.db' && systemctl start finance-bot.service\""
}

print_rollback() {
  if [ "$DB_TOUCHED" = 0 ]; then
    echo "database was not touched, so there is nothing to roll back"
  elif [ "$HAS_BACKUP" = 1 ]; then
    echo "rollback, database only (the code is not backed up), paste on your Mac:"
    rollback_line
  else
    echo "no database backup on the server, so there is nothing to roll back"
  fi
}

DRY=0
if [ "$#" -eq 1 ] && [ "$1" = "--dry-run" ]; then
  DRY=1
elif [ "$#" -ne 0 ]; then
  echo "usage: app/deploy/deploy.sh [--dry-run]" >&2
  exit 2
fi

changes="$(git -C "$ROOT" status --porcelain -- app)"
if [ -n "$changes" ]; then
  echo "refusing to deploy: uncommitted changes under app/ (commit them first)" >&2
  exit 1
fi

# Prints the step; runs its command, or only prints the command under --dry-run.
step() {
  printf '\n== %s\n' "$1"
  shift
  if [ "$DRY" = 1 ]; then
    printf '   %s\n' "$*"
  else
    "$@"
  fi
}

# From the first copy on, a failure says what to roll back: nothing before step 7 touches the database.
trap 'echo "deploy failed." >&2; print_rollback >&2' ERR

if [ "$DRY" = 1 ]; then echo "dry run: nothing is copied, backed up, installed or restarted"; fi

step "1/8 copy app/ to $HOST:$APP (except .env, data/, .venv/, __pycache__/)" \
  rsync -az --exclude .env --exclude data/ --exclude .venv/ --exclude __pycache__/ "$ROOT/app/" "$HOST:$APP/"

step "2/8 back up data/finbot.db to $BACKUP (owner-only, umask 077)" \
  ssh "$HOST" "umask 077 && mkdir -p '$BACKUP' && if [ -f '$APP/data/finbot.db' ]; then python3 -c 'import sqlite3,sys; sqlite3.connect(sys.argv[1]).backup(sqlite3.connect(sys.argv[2]))' '$APP/data/finbot.db' '$BACKUP/finbot.db'; fi"
# Read-only check: the rollback line is offered only once the backup file exists on the server.
if [ "$DRY" = 0 ] && ssh "$HOST" "test -f '$BACKUP/finbot.db'"; then HAS_BACKUP=1; fi

step "3/8 create or update the server venv from requirements.txt" \
  ssh "$HOST" "cd '$APP' && { [ -x .venv/bin/python ] || python3 -m venv .venv; } && .venv/bin/pip install -q -r requirements.txt"

step "4/8 run pytest -q on the server copy, dev requirements in a temporary venv" \
  ssh "$HOST" "set -e; cd '$APP'; t=\$(mktemp -d); trap 'rm -rf \"\$t\"' EXIT; python3 -m venv \"\$t\"; \"\$t/bin/pip\" install -q -r requirements-dev.txt; \"\$t/bin/pytest\" -q"

step "5/8 check the server .env has non-empty BOT_TOKEN and OWNER_ID and mode 600 (values are not printed), and report AI key present or missing (never fails on it)" \
  ssh "$HOST" "if grep -q '^ANTHROPIC_API_KEY=.' '$APP/.env'; then echo 'AI key: present'; else echo 'AI key: missing'; fi; grep -q '^BOT_TOKEN=.' '$APP/.env' && grep -q '^OWNER_ID=.' '$APP/.env' && { [ \"\$(stat -c %a '$APP/.env')\" = 600 ] || { echo 'server .env must have mode 600. Fix it: chmod 600 $APP/.env' >&2; exit 1; }; }"

step "6/8 check deploy/deploy.sh is executable on the server" \
  ssh "$HOST" "test -x '$APP/deploy/deploy.sh'"

# From step 7 the new bot runs against the database, so a failure from here on needs the rollback line.
DB_TOUCHED=1
step "7/8 install units, daemon-reload, enable and restart finance-bot.service, enable the daily timer" \
  ssh "$HOST" "cp '$APP/deploy/finance-bot.service' '$APP/deploy/finance-bot-daily.service' '$APP/deploy/finance-bot-daily.timer' /etc/systemd/system/ && systemctl daemon-reload && systemctl enable finance-bot.service && systemctl restart finance-bot.service && systemctl enable --now finance-bot-daily.timer"

step "8/8 wait 10 seconds (longer than RestartSec=5), then check finance-bot.service is active with NRestarts 0 and finance-bot-daily.timer is active" \
  ssh "$HOST" "sleep 10; n=\$(systemctl show -p NRestarts --value finance-bot.service); echo \"finance-bot.service: \$(systemctl is-active finance-bot.service), NRestarts \$n\"; echo \"finance-bot-daily.timer: \$(systemctl is-active finance-bot-daily.timer)\"; systemctl is-active --quiet finance-bot.service && test \"\$n\" = 0 && systemctl is-active --quiet finance-bot-daily.timer"

if [ "$DRY" = 1 ]; then
  echo "dry run, would print after a real backup (not printed by this run):"
  rollback_line
else
  print_rollback
fi
