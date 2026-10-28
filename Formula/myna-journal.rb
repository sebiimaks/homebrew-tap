class MynaJournal < Formula
  desc "Terminal journal with editable word wrap, themes, and encrypted notes"
  homepage "https://github.com/sebiimaks/MynaJournal"
  url "https://github.com/sebiimaks/MynaJournal/releases/download/v0.20.0/myna-journal_0.20.0_macos-arm64.tar.gz"
  sha256 "6103c8bffb9f2d76edf458022ee4cca2099e0a94e2e28c38cd1e036f037131af"
  license "MIT"

  depends_on arch: :arm64
  depends_on :macos

  def install
    bin.install "mjournal"
    doc.install "LICENSE", "ATTRIBUTION.md", "THIRD_PARTY_NOTICES.txt", "README.md",
                "CONFIGURATION.md", "FILE-BACKEND.md", "THEMES.md", "NOTE-LOCKING.md", "BACKUPS.md"
  end

  test do
    assert_equal "myna-journal #{version}", shell_output("#{bin}/mjournal --version").strip
    assert_path_exists doc/"BACKUPS.md"
    expected_licenses = "MynaJournal license\n\n" + (doc/"LICENSE").read + "\n\n" +
                        (doc/"ATTRIBUTION.md").read + "\n\n" + (doc/"THIRD_PARTY_NOTICES.txt").read
    assert_equal expected_licenses, shell_output("#{bin}/mjournal licenses")
  end
end
