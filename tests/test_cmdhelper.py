"""
Unit tests for CMDHELPER logic, database, search, and placeholder parsing.
"""

import unittest
import tempfile
from pathlib import Path
from cmdhelper_app.db import CommandDatabase, extract_placeholders


class TestCmdHelper(unittest.TestCase):
    def test_extract_placeholders(self):
        cmd = "rsync -avz -e 'ssh -p {porta}' {sorgente} {utente}@{host_remoto}:{destinazione}"
        placeholders = extract_placeholders(cmd)
        self.assertEqual(placeholders, ["porta", "sorgente", "utente", "host_remoto", "destinazione"])

        # Test deduplication
        cmd_dup = "ping {host} && echo {host}"
        self.assertEqual(extract_placeholders(cmd_dup), ["host"])

        # Test no placeholders
        self.assertEqual(extract_placeholders("ls -l /var/log"), [])

    def test_database_crud(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_commands.json"
            db = CommandDatabase(file_path=test_file)

            # Check default commands loaded
            self.assertGreater(len(db.commands), 10)
            categories = db.get_categories()
            self.assertIn("Tutti i comandi", categories)
            self.assertIn("Rete & SSH", categories)

            # Test search query
            results = db.filter(query="ping")
            self.assertTrue(any("ping" in c.get("title", "").lower() or "ping" in c.get("command", "").lower() for c in results))

            # Test filter by category
            net_results = db.filter(category="Rete & SSH")
            for c in net_results:
                self.assertEqual(c["category"], "Rete & SSH")

            # Test Add Command
            new_cmd = db.add_command(
                title="Test Backup",
                category="Custom",
                command_str="tar -cvf {archive}.tar {source}",
                description="Test description",
                tags=["test", "backup"]
            )
            self.assertIsNotNone(new_cmd["id"])

            # Reload database from disk
            db2 = CommandDatabase(file_path=test_file)
            found = db2.filter(query="Test Backup")
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["command"], "tar -cvf {archive}.tar {source}")

            # Test Update
            cmd_id = new_cmd["id"]
            db2.update_command(cmd_id, {"title": "Test Backup Updated"})
            db3 = CommandDatabase(file_path=test_file)
            found_updated = db3.filter(query="Test Backup Updated")
            self.assertEqual(len(found_updated), 1)

            # Test Delete
            db3.delete_command(cmd_id)
            db4 = CommandDatabase(file_path=test_file)
            found_deleted = db4.filter(query="Test Backup Updated")
            self.assertEqual(len(found_deleted), 0)


if __name__ == "__main__":
    unittest.main()
