import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from codegen.generate import _build_config, _finish_package
from hyperflow._client import DEFAULT_URL

class EndpointTests(unittest.TestCase):
    def test_runtime_and_codegen_use_the_canonical_endpoint(self) -> None:
        root = Path(__file__).parents[1]
        url = "https://api.hyperflowlabs.com/graphql"
        self.assertIn(f'remote_schema_url = "{url}"',
                      (root / "codegen" / "ariadne.toml").read_text())
        self.assertIn(f'DEFAULT_URL = "{url}"',
                      (root / "codegen" / "include" / "_client.py").read_text())
        expected = os.getenv("HYPERFLOW_EXPECTED_API_URL", url)
        self.assertEqual(DEFAULT_URL, expected)

    def test_schema_file_and_runtime_endpoint_overrides(self) -> None:
        with patch.dict(os.environ, {
            "HYPERFLOW_SCHEMA_PATH": "stage-schema.graphql",
            "HYPERFLOW_DEFAULT_API_URL": "https://stage.api.hyperflowlabs.com/graphql",
        }):
            config = _build_config()
            try:
                text = Path(config).read_text()
                self.assertIn("schema_path = ", text)
                self.assertIn("stage-schema.graphql", text)
                self.assertNotIn("remote_schema_url =", text)
                with tempfile.TemporaryDirectory() as directory:
                    package = Path(directory) / "src" / "hyperflow"
                    package.mkdir(parents=True)
                    (package / "__init__.py").write_text("")
                    (package / "_client.py").write_text('DEFAULT_URL = "production"\n')
                    with patch("codegen.generate.ROOT", Path(directory)):
                        _finish_package()
                    self.assertIn("https://stage.api.hyperflowlabs.com/graphql",
                                  (package / "_client.py").read_text())
            finally:
                os.unlink(config)


if __name__ == "__main__":
    unittest.main()
