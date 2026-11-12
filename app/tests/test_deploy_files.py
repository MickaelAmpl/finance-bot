import os
import re
import shutil
import subprocess
from pathlib import Path

DEPLOY = Path(__file__).resolve().parent.parent / "deploy"
SCRIPT = DEPLOY / "deploy.sh"
TOKEN_LIKE = re.compile(r"\d{6,}:[A-Za-z0-9_-]{20,}")


def assert_has_lines(name: str, expected: list[str]) -> None:
    present = (DEPLOY / name).read_text().splitlines()
    missing = [line for line in expected if line not in present]
    assert not missing, f"{name} is missing {missing}"


def test_service_unit_lines():
    assert_has_lines(
        "finance-bot.service",
        [
            "[Unit]",
            "After=network-online.target",
            "Wants=network-online.target",
            "[Service]",
            "UMask=0077",
            "WorkingDirectory=/opt/finance-bot",
            "EnvironmentFile=/opt/finance-bot/.env",
            "ExecStart=/opt/finance-bot/.venv/bin/python -m finbot",
            "Restart=always",
            "RestartSec=5",
            "[Install]",
            "WantedBy=multi-user.target",
        ],
    )


def test_daily_service_unit_lines():
    assert_has_lines(
        "finance-bot-daily.service",
        [
            "[Unit]",
            "After=network-online.target",
            "Wants=network-online.target",
            "[Service]",
            "UMask=0077",
            "Type=oneshot",
            "WorkingDirectory=/opt/finance-bot",
            "EnvironmentFile=/opt/finance-bot/.env",
            "ExecStart=/opt/finance-bot/.venv/bin/python -m finbot.jobs daily",
        ],
    )


def test_daily_timer_unit_lines():
    assert_has_lines(
        "finance-bot-daily.timer",
        [
            "[Timer]",
            "OnCalendar=*-*-* 09:00:00 Europe/Vienna",
            "Persistent=true",
            "Unit=finance-bot-daily.service",
            "[Install]",
            "WantedBy=timers.target",
        ],
    )


def test_deploy_script_is_valid_bash():
    result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_deploy_script_has_dry_run_and_excludes():
    text = SCRIPT.read_text()
    for needle in ["--dry-run", "--exclude .env", "--exclude data/"]:
        assert needle in text, needle


def test_deploy_script_has_no_token():
    assert TOKEN_LIKE.search(SCRIPT.read_text()) is None


def test_deploy_script_is_executable():
    assert os.access(SCRIPT, os.X_OK)


def test_deploy_script_enables_bot_service():
    assert "systemctl enable finance-bot.service" in SCRIPT.read_text()


def test_deploy_script_tests_backup_before_rollback_rm():
    lines = [line for line in SCRIPT.read_text().splitlines() if "rm -f" in line]
    assert lines, "no rollback line with rm -f"
    assert lines[0].index("test -f") < lines[0].index("rm -f")


def step_8_command() -> str:
    lines = SCRIPT.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith('step "8/8'))
    return "\n".join(lines[start : start + 2])


def test_deploy_step_8_checks_restarts_and_timer_after_sleep():
    cmd = step_8_command()
    needles = [
        "sleep 10",
        "systemctl show -p NRestarts --value finance-bot.service",
        "systemctl is-active --quiet finance-bot.service",
        r"test \"\$n\" = 0",
        "systemctl is-active --quiet finance-bot-daily.timer",
    ]
    for needle in needles:
        assert needle in cmd, needle
    positions = [cmd.index(needle) for needle in needles]
    assert positions == sorted(positions), "sleep, NRestarts check, then the services, in order"
    assert "is-active finance-bot.service finance-bot-daily.timer" not in cmd


def test_deploy_script_sets_db_flag_before_step_7():
    lines = SCRIPT.read_text().splitlines()
    assert "DB_TOUCHED=1" in lines, "no DB_TOUCHED=1 line"
    step7 = next(i for i, line in enumerate(lines) if line.startswith('step "7/8'))
    assert lines.index("DB_TOUCHED=1") < step7, "DB_TOUCHED=1 must come before step 7"


def test_deploy_script_checks_env_mode_600():
    text = SCRIPT.read_text()
    assert "stat -c %a" in text
    assert "chmod 600 $APP/.env" in text


FAKE_REMOTE_SSH = """#!/bin/sh
for cmd; do :; done
case "$cmd" in
  *BOT_TOKEN*) exec bash -c "$(printf '%s' "$cmd" | sed "s#/opt/finance-bot#$FAKE_SERVER#g")" ;;
esac
exit 0
"""

FAKE_REMOTE_STAT = """#!/bin/sh
python3 -c 'import os,stat,sys; print(format(stat.S_IMODE(os.stat(sys.argv[1]).st_mode), "o"))' "$3"
"""


def run_deploy_with_fake_remote(tmp_path: Path, env_text: str) -> subprocess.CompletedProcess[str]:
    repo = tmp_path / "repo"
    script = repo / "app" / "deploy" / "deploy.sh"
    script.parent.mkdir(parents=True)
    shutil.copy2(SCRIPT, script)
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    identity = ["-c", "user.name=test", "-c", "user.email=test@test"]
    subprocess.run(["git", "-C", str(repo), *identity, "add", "app"], check=True)
    subprocess.run(["git", "-C", str(repo), *identity, "commit", "-q", "-m", "init"], check=True)

    server = tmp_path / "server"
    (server / "deploy").mkdir(parents=True)
    shutil.copy2(SCRIPT, server / "deploy" / "deploy.sh")
    env_file = server / ".env"
    env_file.write_text(env_text)
    env_file.chmod(0o600)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fakes = {"ssh": FAKE_REMOTE_SSH, "stat": FAKE_REMOTE_STAT, "rsync": "#!/bin/sh\nexit 0\n"}
    for name, body in fakes.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)

    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_SERVER": str(server),
    }
    return subprocess.run([str(script)], env=env, capture_output=True, text=True, timeout=60)


def test_deploy_step_5_reports_ai_key_present_without_printing_it(tmp_path: Path) -> None:
    result = run_deploy_with_fake_remote(
        tmp_path, "BOT_TOKEN=1:x\nOWNER_ID=1\nANTHROPIC_API_KEY=sk-ant-test-0000\n"
    )
    assert result.returncode == 0, result.stderr
    assert "AI key: present" in result.stdout
    assert "sk-ant-test-0000" not in result.stdout + result.stderr


def test_deploy_step_5_reports_ai_key_missing_when_empty_or_absent(tmp_path: Path) -> None:
    shapes = ("BOT_TOKEN=1:x\nOWNER_ID=1\n", "BOT_TOKEN=1:x\nOWNER_ID=1\nANTHROPIC_API_KEY=\n")
    for index, env_text in enumerate(shapes):
        result = run_deploy_with_fake_remote(tmp_path / str(index), env_text)
        assert result.returncode == 0, result.stderr
        assert "AI key: missing" in result.stdout


def test_deploy_step_5_still_fails_without_bot_token(tmp_path: Path) -> None:
    result = run_deploy_with_fake_remote(
        tmp_path, "OWNER_ID=1\nANTHROPIC_API_KEY=sk-ant-test-0000\n"
    )
    assert result.returncode != 0
    assert "deploy failed." in result.stderr
