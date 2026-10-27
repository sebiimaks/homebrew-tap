import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("update_formula", Path(__file__).with_name("update-formula.py"))
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


def release(version="0.19.0"):
    return {
        "tag_name": f"v{version}", "draft": False, "prerelease": False,
        "assets": [{
            "name": name, "state": "uploaded",
            "browser_download_url": f"{updater.DOWNLOAD_ROOT}/v{version}/{name}",
        } for name in (updater.archive_name(version), "SHA256SUMS")],
    }


def formula(version="0.19.0", checksum="a" * 64):
    return (f'class MynaJournal < Formula\n  url "{updater.archive_url(version)}"\n'
            f'  sha256 "{checksum}"\n'
            '  license "MIT"\n  def install\n    bin.install "mjournal"\n  end\nend\n')


class ReleaseValidationTests(unittest.TestCase):
    def test_published_stable_release_with_required_assets_is_accepted(self):
        self.assertEqual(updater.release_version(release()), "0.19.0")

    def test_draft_prerelease_and_malformed_tags_are_rejected(self):
        for key, value in (("draft", True), ("prerelease", True), ("tag_name", "0.19.0"),
                           ("tag_name", "v0.19.0-rc1"), ("tag_name", "v00.19.0"),
                           ("tag_name", "v0.19.0\nrun something")):
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                candidate = release()
                candidate[key] = value
                updater.release_version(candidate)

    def test_missing_duplicate_incomplete_and_foreign_assets_are_rejected(self):
        candidates = []
        missing = release()
        missing["assets"].pop()
        candidates.append(missing)
        duplicate = release()
        duplicate["assets"].append(copy.deepcopy(duplicate["assets"][0]))
        candidates.append(duplicate)
        incomplete = release()
        incomplete["assets"][0]["state"] = "starter"
        candidates.append(incomplete)
        foreign = release()
        foreign["assets"][0]["browser_download_url"] = "https://example.com/malicious.tar.gz"
        candidates.append(foreign)
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                updater.release_version(candidate)


class ChecksumValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.archive = Path(self.directory.name) / "archive.tar.gz"
        self.archive.write_bytes(b"a verified release archive")
        self.checksum = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.name = updater.archive_name("0.19.0")

    def test_archive_is_verified_against_its_exact_checksum_entry(self):
        sums = f"{'b' * 64}  unrelated.deb\n{self.checksum}  {self.name}\n"
        self.assertEqual(updater.verified_checksum(sums, self.archive, self.name), self.checksum)

    def test_checksum_mismatch_missing_duplicate_or_malformed_entries_fail(self):
        valid = f"{self.checksum}  {self.name}\n"
        for sums in (f"{'0' * 64}  {self.name}\n", f"{self.checksum}  wrong-name\n",
                     valid * 2, f"invalid  {self.name}\n"):
            with self.subTest(sums=sums), self.assertRaises(ValueError):
                updater.verified_checksum(sums, self.archive, self.name)


class FormulaUpdateTests(unittest.TestCase):
    def test_same_release_is_a_byte_for_byte_noop(self):
        original = formula()
        self.assertEqual(updater.updated_formula(original, "0.19.0", "a" * 64), original)

    def test_upgrade_changes_only_url_and_checksum(self):
        self.assertEqual(updater.updated_formula(formula(), "0.20.0", "b" * 64), formula("0.20.0", "b" * 64))

    def test_versions_are_compared_numerically(self):
        self.assertEqual(updater.updated_formula(formula("0.9.0"), "0.10.0", "b" * 64), formula("0.10.0", "b" * 64))

    def test_downgrade_and_replaced_same_version_archive_are_rejected(self):
        for version, checksum in (("0.18.0", "b" * 64), ("0.19.0", "b" * 64)):
            with self.subTest(version=version), self.assertRaises(ValueError):
                updater.updated_formula(formula(), version, checksum)

    def test_ambiguous_or_inconsistent_formula_is_rejected(self):
        candidates = [formula() + f'  url "{updater.archive_url("0.19.0")}"\n',
                      formula().replace(f'  url "{updater.archive_url("0.19.0")}"\n', ""),
                      formula(checksum="invalid")]
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                updater.updated_formula(candidate, "0.20.0", "b" * 64)

    def test_version_is_inferred_from_matching_stable_tag_and_archive_name(self):
        self.assertEqual(updater.formula_values(formula())["version"], "0.19.0")
        for invalid in (formula().replace("/v0.19.0/", "/v0.18.0/"),
                        formula().replace("myna-journal_0.19.0_", "myna-journal_0.20.0_"),
                        formula("0.19.0-rc1"), formula("00.19.0"),
                        formula().replace(".tar.gz", ".tar.gz?download=1"),
                        formula().replace("https://github.com/", "https://example.com/")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                updater.formula_values(invalid)

    def test_explicit_version_override_is_rejected(self):
        for override in ("0.19.0", "0.18.0"):
            with self.subTest(override=override), self.assertRaises(ValueError):
                updater.updated_formula(formula() + f'  version "{override}"\n', "0.20.0", "b" * 64)


if __name__ == "__main__":
    unittest.main()
