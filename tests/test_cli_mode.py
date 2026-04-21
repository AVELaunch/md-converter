import contextlib
import importlib.util
import io
import sys
import types
import unittest
from collections import namedtuple
from pathlib import Path
from unittest import mock


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_DIR / "src" / "converter_app.py"


def load_converter_app(config_text=None):
    webview_stub = types.ModuleType("webview")
    converters_stub = types.ModuleType("converters")
    native_drop_stub = types.ModuleType("native_drop")

    convert_result = namedtuple("ConvertResult", "success output_path word_count message")
    converters_stub.SUPPORTED = {".txt"}
    converters_stub.ConvertResult = convert_result
    converters_stub.route = lambda path, output_dir, vault_dir=None: convert_result(
        True,
        str(output_dir / "example.md"),
        2,
        "OK -> example.md",
    )
    converters_stub.convert_pasted = lambda text, output_dir, vault_dir=None: convert_result(
        True,
        str(output_dir / "pasted.md"),
        len(text.split()),
        "OK -> pasted.md",
    )
    native_drop_stub.setup_native_drop = lambda window, callback: None

    original_modules = {
        name: sys.modules.get(name)
        for name in ("webview", "converters", "native_drop")
    }
    sys.modules["webview"] = webview_stub
    sys.modules["converters"] = converters_stub
    sys.modules["native_drop"] = native_drop_stub

    spec = importlib.util.spec_from_file_location("test_converter_app", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None

    config_path = PROJECT_DIR / "config.json"
    real_exists = Path.exists
    real_read_text = Path.read_text

    def fake_exists(path_obj):
        if config_text is not None and path_obj == config_path:
            return True
        return real_exists(path_obj)

    def fake_read_text(path_obj, *args, **kwargs):
        if config_text is not None and path_obj == config_path:
            return config_text
        return real_read_text(path_obj, *args, **kwargs)

    with mock.patch("pathlib.Path.exists", fake_exists), mock.patch("pathlib.Path.read_text", fake_read_text):
        spec.loader.exec_module(module)

    for name, original in original_modules.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original

    return module


class CliModeTests(unittest.TestCase):
    def test_cli_mode_reports_vault_disabled_when_not_configured(self):
        module = load_converter_app()
        module.VAULT_DIR = None

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.cli_mode(["/tmp/example.txt"])

        text = output.getvalue()
        self.assertIn("SUMMARY: 1/1 converted | 2 total words", text)
        self.assertIn("Vault:  disabled (no config.json)", text)

    def test_cli_mode_displays_url_inputs_without_path_mangling(self):
        module = load_converter_app()
        module.VAULT_DIR = None

        output = io.StringIO()
        url = "https://example.com/article"
        with contextlib.redirect_stdout(output):
            module.cli_mode([url])

        self.assertIn(url, output.getvalue())

    def test_invalid_config_falls_back_to_disabled_vault(self):
        module = load_converter_app(config_text="{invalid json}")
        self.assertIsNone(module.VAULT_DIR)


if __name__ == "__main__":
    unittest.main()
