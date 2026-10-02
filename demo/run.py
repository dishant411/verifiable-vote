"""Load the pinned upstream application, then run the requested local adapter."""
import os
import runpy
import sys
from pathlib import Path
import django

root = Path(__file__).resolve().parents[1]
upstream = Path(os.environ.get('HELIOS_DIR', root / '.runtime/helios')).resolve()
sys.path.insert(0, str(upstream))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_demo'
os.environ.setdefault('DEMO_SECRET_KEY', 'offline-synthetic-evidence-only')
django.setup()
if len(sys.argv) < 2:
    raise SystemExit('Specify election_demo or verify_record')
module = sys.argv.pop(1)
if module not in ('election_demo', 'verify_record'):
    raise SystemExit('Unknown adapter')
runpy.run_module(module, run_name='__main__')
