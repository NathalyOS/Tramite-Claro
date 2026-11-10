import importlib.util
import sys
from pathlib import Path

src = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src))

spec = importlib.util.spec_from_file_location("tramite_claro_app", src / "app.py")
modulo = importlib.util.module_from_spec(spec)
sys.modules["tramite_claro_app"] = modulo
spec.loader.exec_module(modulo)
app = modulo.app
