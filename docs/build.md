# Building the experimental source snapshot

These recipes were adapted from the development build environment. Syntax, pinned revisions and patch application are checked; a full build from a fresh clone of this publication has not yet been completed. Budget several hundred GB of free SSD space. The current defaults use eight build jobs, a 20 GiB container memory limit and up to 40 GiB including swap; actual host swap must exist for that allowance to help.

Use an x86-64 Linux host with Docker, Git, Git LFS, Python 3.11+, and Android's `repo` command installed. Vendor regeneration runs on the host and uses the pinned extract-tools binaries. Build packages and Java are installed in the container.

```sh
git clone https://github.com/michielryvers/lineage-tb128fu.git
cd lineage-tb128fu
docker build -t lenovo-lineage-build:24.04 -f rom-build/Containerfile .
bash scripts/sync.sh
python3 scripts/fetch-drivers.py
python3 rom-build/prepare-source.py
bash rom-build/build-rom.sh
```

`sync.sh` initializes from this checkout's exact committed manifest revision. All Android projects are pinned. After a successful sync it saves the resolved manifest to `build/records/source-manifest.xml`. Do not copy local manifests from another Android checkout into this build.

The three source forks already contain our device and kernel changes. `prepare-source.py` verifies their revisions and applies only the four remaining platform patches; it also stages hash-verified GPU donors, isolates the legacy C2D dependency and regenerates vendor makefiles. Never apply the historical device/kernel patches on top again.

Build resources can be overridden with `BUILD_JOBS`, `BUILD_MEMORY`, `BUILD_MEMORY_SWAP`, and `GO_MEMORY_LIMIT`. Sync concurrency uses `SYNC_JOBS`. For example:

```sh
BUILD_JOBS=8 BUILD_MEMORY=24g BUILD_MEMORY_SWAP=40g GO_MEMORY_LIMIT=16GiB bash rom-build/build-rom.sh
```

WebView is materialized from Git LFS and hash-checked before building. Outputs are under `build/lineage/out/target/product/tb128fu/`. The container base and package repositories are not frozen, so this is a pinned-source recipe, not a claim of bit-for-bit reproducibility.

Build output uses development signing defaults. No public flashing procedure is provided until recovery, OTA post-install, A/B switching and a clean installation of the combined build have been verified. Google applications are a separate integration and are not bundled by these scripts.
