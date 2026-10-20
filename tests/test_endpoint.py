import unittest
from pathlib import Path

class EndpointTests(unittest.TestCase):
    def test_runtime_and_codegen_use_the_canonical_endpoint(self) -> None:
        root = Path(__file__).parents[1]
        url = "https://api.hyperflowlabs.com/graphql"
        self.assertIn(f'remote_schema_url = "{url}"',
                      (root / "codegen" / "ariadne.toml").read_text())
        self.assertIn(f'DEFAULT_URL = "{url}"',
                      (root / "codegen" / "include" / "_client.py").read_text())


if __name__ == "__main__":
    unittest.main()
