#!/usr/bin/env python3
"""Update the formula from a verified, stable MynaJournal GitHub release."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPOSITORY = "sebiimaks/MynaJournal"
DOWNLOAD_ROOT = f"https://github.com/{REPOSITORY}/releases/download"
VERSION_PATTERN = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
FORMULA = Path(__file__).resolve().parent.parent / "Formula/myna-journal.rb"


def version_tuple(version):
    if not isinstance(version, str) or re.fullmatch(VERSION_PATTERN, version) is None:
        raise ValueError("Expected a stable version in X.Y.Z form")
    return tuple(map(int, version.split(".")))


def archive_name(version):
    return f"myna-journal_{version}_macos-arm64.tar.gz"


def archive_url(version):
    return f"{DOWNLOAD_ROOT}/v{version}/{archive_name(version)}"


def release_version(release):
    if not isinstance(release, dict):
        raise ValueError("Invalid GitHub release metadata")
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("Only published stable releases are eligible")
    tag = release.get("tag_name", "")
    if not isinstance(tag, str) or not tag.startswith("v"):
        raise ValueError("Expected a release tag beginning with v")
    version = tag[1:]
    version_tuple(version)
    assets = release.get("assets")
    if not isinstance(assets, list) or not all(isinstance(asset, dict) for asset in assets):
        raise ValueError("Invalid release asset list")
    for name in (archive_name(version), "SHA256SUMS"):
        matches = [asset for asset in assets if asset.get("name") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one release asset named {name}")
        asset = matches[0]
        expected_url = f"{DOWNLOAD_ROOT}/{tag}/{name}"
        if asset.get("browser_download_url") != expected_url or asset.get("state") != "uploaded":
            raise ValueError(f"Unexpected or incomplete release asset: {name}")
    return version


def verified_checksum(checksums, archive, name):
    matches = []
    for line in checksums.splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64}) [ *](.+)", line)
        if match is None:
            raise ValueError("Malformed SHA256SUMS entry")
        if match[2] == name:
            matches.append(match[1].lower())
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one checksum for {name}")
    digest = hashlib.sha256()
    with archive.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != matches[0]:
        raise ValueError(f"Downloaded archive does not match SHA256SUMS: {name}")
    return matches[0]


def formula_values(formula):
    values = {}
    for field in ("url", "version", "sha256"):
        matches = re.findall(rf'^  {field} "([^"\n]+)"$', formula, flags=re.MULTILINE)
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one top-level {field} in formula")
        values[field] = matches[0]
    version_tuple(values["version"])
    if values["url"] != archive_url(values["version"]):
        raise ValueError("Existing formula URL does not match its version")
    if re.fullmatch(r"[0-9a-f]{64}", values["sha256"]) is None:
        raise ValueError("Invalid existing formula SHA256")
    return values


def updated_formula(formula, version, checksum):
    current = formula_values(formula)
    if version_tuple(version) < version_tuple(current["version"]):
        raise ValueError("Refusing to downgrade the formula")
    if re.fullmatch(r"[0-9a-f]{64}", checksum) is None:
        raise ValueError("Invalid new formula SHA256")
    if version == current["version"]:
        if checksum != current["sha256"]:
            raise ValueError("The published archive changed without a version change")
        return formula
    for field, value in (("url", archive_url(version)), ("version", version), ("sha256", checksum)):
        formula = re.sub(rf'^  {field} "[^"\n]+"$', f'  {field} "{value}"', formula, flags=re.MULTILINE)
    return formula


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report an available update without modifying the formula")
    args = parser.parse_args()
    formula = FORMULA.read_text(encoding="utf-8")
    current = formula_values(formula)
    release = json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{REPOSITORY}/releases/latest"], text=True,
    ))
    version = release_version(release)
    if version_tuple(version) < version_tuple(current["version"]):
        raise ValueError("Latest release is older than the installed formula; refusing downgrade")
    name = archive_name(version)
    with tempfile.TemporaryDirectory(prefix="mynajournal-tap-") as directory:
        subprocess.run([
            "gh", "release", "download", f"v{version}", "--repo", REPOSITORY,
            "--pattern", name, "--pattern", "SHA256SUMS", "--dir", directory,
        ], check=True)
        downloaded = Path(directory)
        checksum = verified_checksum(
            (downloaded / "SHA256SUMS").read_text(encoding="ascii"), downloaded / name, name,
        )
    updated = updated_formula(formula, version, checksum)
    if updated == formula:
        print(f"MynaJournal {version} is already current; archive checksum verified.")
        return 0
    if args.check:
        print(f"MynaJournal {version} is available (formula has {current['version']}).")
        return 1
    FORMULA.write_text(updated, encoding="utf-8")
    print(f"Updated MynaJournal from {current['version']} to {version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Formula update failed: {error}") from error
