import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "security-scan.py"
spec = importlib.util.spec_from_file_location("security_scan", MODULE_PATH)
security_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(security_scan)


def test_parse_json_valid():
    assert security_scan.parse_json('{"ok": true}') == {"ok": True}


def test_parse_json_invalid():
    assert security_scan.parse_json("not json") is None


def test_scan_target_missing_tools(tmp_path, monkeypatch):
    monkeypatch.setattr(security_scan.shutil, "which", lambda _: None)
    result = security_scan.scan_target(tmp_path)

    assert result["overall_status"] == "FAIL"
    assert all(
        item["status"] == "NOT_INSTALLED"
        for item in result["checks"].values()
    )
