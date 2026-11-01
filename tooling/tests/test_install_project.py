"""La instalación no toca archivos ajenos ni requiere configuración global."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "install_project", Path(__file__).resolve().parents[1] / "install-project.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ProjectInstallTests(unittest.TestCase):
    def test_unmanaged_conflict_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            source = root / "generated.md"
            source.write_text("new")
            target = project / ".opencode/agents/a.md"
            target.parent.mkdir(parents=True)
            target.write_text("project-owned")
            with patch.object(installer, "mappings", return_value={Path(".opencode/agents/a.md"): source}):
                with self.assertRaisesRegex(ValueError, "no gestionado"):
                    installer.run(project, True)
            self.assertEqual("project-owned", target.read_text())
            self.assertFalse((project / installer.RECEIPT).exists())

    def test_apply_creates_project_bundle_and_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()
            source = root / "generated.md"
            source.write_text("generated")
            mapping = {Path(".opencode/agents/a.md"): source}
            with patch.object(installer, "mappings", return_value=mapping):
                installer.run(project, False)
                self.assertFalse((project / installer.RECEIPT).exists())
                installer.run(project, True)
            self.assertEqual("generated", (project / ".opencode/agents/a.md").read_text())
            self.assertEqual("master-orchestrator",
                             json.loads((project / ".opencode/opencode.json").read_text())["default_agent"])
            receipt = json.loads((project / installer.RECEIPT).read_text())
            self.assertIn(".opencode/agents/a.md", receipt["files"])
            self.assertTrue((project / ".opencode/.foundry/.gitignore").is_file())

    def test_receipt_cannot_delete_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            (project / ".opencode").mkdir(parents=True)
            outside = root / "outside.txt"
            outside.write_text("keep")
            (project / installer.RECEIPT).write_text(json.dumps({"files": {"../outside.txt": "bad"}}))
            with patch.object(installer, "mappings", return_value={Path(".opencode/agents/a.md"): outside}):
                with self.assertRaisesRegex(ValueError, "destino no permitido"):
                    installer.run(project, True)
            self.assertEqual("keep", outside.read_text())


if __name__ == "__main__":
    unittest.main()
