# Keeping up with upstream

Yes: these are normal GitHub forks with original ancestry. Device changes are separate commits and the kernel keeps the Motorola integration merge, so future updates can be reviewed against their original sources.

Run `python3 scripts/check-upstream.py` for a read-only comparison of recorded upstream bases with current branch heads. It does not modify sources, pins or the tablet. It covers the principal device/kernel/Lineage manifest entry points, not every Android subproject or vendor release. No scheduled merging or flashing is enabled.

For a device or kernel checkout, configure the upstream URL from `provenance/forks.json`, fetch it, and create a review branch from `codex/lineage-24.0`:

```sh
git fetch upstream
git switch codex/lineage-24.0
git switch -c codex/upstream-update
# Choose and review the correct upstream branch before merging it.
git merge upstream/16.2
```

`16.2` above is the original device-tree branch. The Lenovo kernel uses `master`; the additional Motorola kernel donor uses `lineage-24.0`. Treat these as different inputs: donor changes must retain the Lenovo board-specific fixes. Do not force-sync a development branch or replace the Lenovo kernel blindly with a donor tree.

For an Android platform refresh, first inspect LineageOS's updated manifest in a separate integration workspace, sync the desired release branch, and export a newly resolved manifest with `repo manifest -r`. Re-apply/review the four platform patches against their new bases. Update `rom-build/patches/revisions.json`, the three fork pins, `provenance/forks.json`, `provenance/upstreams.json` and `manifests/pinned.xml` together. Keep absolute remote URLs and all commit pins. Review vendor changes separately.

Build and test the complete combined image. Cover clean install, upgrade, slot changes, recovery, Wi-Fi, Bluetooth, audio/video, UI rendering, sleep/wake and extended idle. Merge reviewed source changes, then commit the new manifest and tag it with any eventual ROM release. Existing tagged manifests remain unchanged.

References: [GitHub fork synchronization](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/syncing-a-fork), [Android repo manifest format](https://gerrit.googlesource.com/git-repo/+/HEAD/docs/manifest-format.md).
