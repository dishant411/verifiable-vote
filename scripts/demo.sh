#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UPSTREAM_SHA=88621e3196961ec03fe54bbd3a1c2196e715e9a2
export HELIOS_DIR="${HELIOS_DIR:-$ROOT/.runtime/helios}"
export PYTHONPATH="$ROOT/demo:$HELIOS_DIR${PYTHONPATH:+:$PYTHONPATH}"
export DJANGO_SETTINGS_MODULE=settings_demo
mkdir -p "$ROOT/.runtime"
action="${1:-serve}"
if [ "$#" -gt 0 ]; then shift; fi
if [ "$action" = setup ]; then
  command -v "${UV:-uv}" >/dev/null || { echo 'Install uv from https://docs.astral.sh/uv/getting-started/installation/'; exit 1; }
  if [ ! -d "$HELIOS_DIR/.git" ]; then
    git clone https://github.com/benadida/helios-server.git "$HELIOS_DIR"
    git -C "$HELIOS_DIR" checkout --detach "$UPSTREAM_SHA"
  fi
  [ "$(git -C "$HELIOS_DIR" rev-parse HEAD)" = "$UPSTREAM_SHA" ] || { echo 'Unexpected upstream revision'; exit 1; }
  "${UV:-uv}" sync --project "$HELIOS_DIR" --frozen
  if [ ! -f "$ROOT/.runtime/secret" ]; then
    "$HELIOS_DIR/.venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(48))' > "$ROOT/.runtime/secret"
    chmod 600 "$ROOT/.runtime/secret"
  fi
fi
[ -x "$HELIOS_DIR/.venv/bin/python" ] || { echo 'Run ./scripts/demo.sh setup first'; exit 1; }
[ "$(git -C "$HELIOS_DIR" rev-parse HEAD)" = "$UPSTREAM_SHA" ] || { echo 'Unexpected upstream revision'; exit 1; }
export DEMO_SECRET_KEY="$(cat "$ROOT/.runtime/secret")"
cd "$HELIOS_DIR"
case "$action" in
  setup) exec .venv/bin/python manage.py migrate --noinput ;;
  serve) .venv/bin/python "$ROOT/demo/run.py" election_demo seed
         exec .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload ;;
  sample) exec .venv/bin/python "$ROOT/demo/run.py" election_demo sample --short-name=synthetic-audit-sample-v2 "$@" ;;
  export) exec .venv/bin/python "$ROOT/demo/run.py" election_demo export "$@" ;;
  verify) exec .venv/bin/python "$ROOT/demo/run.py" verify_record "$@" ;;
  test) exec .venv/bin/python manage.py test test_demo --verbosity=2 ;;
  upstream-tests) exec .venv/bin/python manage.py test helios helios_auth --settings=settings_validation --verbosity=1 ;;
  *) echo 'Usage: demo.sh setup|serve|sample|export|verify|test|upstream-tests'; exit 1 ;;
esac
