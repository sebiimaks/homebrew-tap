class MynaJournal < Formula
  desc "Terminal journal with editable word wrap, themes, and encrypted notes"
  homepage "https://github.com/sebiimaks/MynaJournal"
  url "https://github.com/sebiimaks/MynaJournal/releases/download/v0.24.3/myna-journal_0.24.3_macos-arm64.tar.gz"
  sha256 "d05979e4831660c5f1c67e0cc953a2a6959347a46d6454cdc35f3b07bc647d9b"
  license "MIT"

  depends_on arch: :arm64
  depends_on :macos

  def install
    bin.install "mjournal"
    doc.install "LICENSE", "ATTRIBUTION.md", "THIRD_PARTY_NOTICES.txt", "README.md",
                "CONFIGURATION.md", "FILE-BACKEND.md", "THEMES.md", "NOTE-LOCKING.md", "JOURNAL-LOCKING.md",
                "BACKUPS.md"
  end

  test do
    assert_equal "myna-journal #{version}", shell_output("#{bin}/mjournal --version").strip
    assert_path_exists doc/"BACKUPS.md"
    assert_path_exists doc/"JOURNAL-LOCKING.md"
    expected_licenses = "MynaJournal license\n\n" + (doc/"LICENSE").read + "\n\n" +
                        (doc/"ATTRIBUTION.md").read + "\n\n" + (doc/"THIRD_PARTY_NOTICES.txt").read
    assert_equal expected_licenses, shell_output("#{bin}/mjournal licenses")
  end
end
