class MynaJournal < Formula
  desc "Terminal journal with editable word wrap, themes, and encrypted notes"
  homepage "https://github.com/sebiimaks/MynaJournal"
  url "https://github.com/sebiimaks/MynaJournal/releases/download/v0.21.0/myna-journal_0.21.0_macos-arm64.tar.gz"
  sha256 "cae34ca2fd0476dda25d6d8c33e20482058b29dbbb4be2600402e44b3fcc9a97"
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
