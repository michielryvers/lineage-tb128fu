# Building the experimental source snapshot

The September 19 integrated source changes completed a full build and upgrade on the development tablet; public fork trees match those patches. These recipes were adapted from that development build environment. Syntax, pinned revisions and patch application are checked; a full build from a fresh clone of this publication has not yet been completed. Budget several hundred GB of free SSD space. The current defaults use eight build jobs, a 20 GiB container memory limit and up to 40 GiB including swap; actual host swap must exist for that allowance to help.

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

Build output uses development signing defaults. The development upgrade verified OTA post-install and A/B switching with the existing development recovery. A public flashing procedure still requires the exact distributable recovery, clean-install and rollback validation. Google applications are a separate integration and are not bundled by these scripts.
