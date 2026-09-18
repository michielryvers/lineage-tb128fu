# Before a binary release

The initial publication intentionally has no downloadable ROM image.

1. Build the complete exported source set from a fresh checkout, record the resolved manifest and toolchain/container identity, and verify the packaged partition sizes and contents.
2. Test a clean installation and an upgrade using the exact published recovery and OTA, including post-install, A/B switching and recovery from a failed boot. Write instructions from that test, not from earlier experimental workarounds.
3. Exercise Bluetooth, Wi-Fi, video, rendering, suspend/resume and overnight idle. Publish remaining problems and the tested hardware model explicitly.
4. Establish release signing and retain private keys outside Git and CI artifacts. Verify recovery contains no personal ADB authorization keys.
5. Review the distribution terms for all included third-party binaries; Google apps remain a separately documented choice unless explicitly handled for that distribution.
6. Tag the source manifest and forks, attach checksums and source/provenance links to the matching GitHub release, and retain the previous release for rollback.

Do not upload development backups or the old partially validated packages as a release.
