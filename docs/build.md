# Building the experimental source snapshot

The September 20 integrated source changes completed an incremental full-ROM build and upgrade on the development tablet; public fork trees match those patches. These recipes were adapted from that development build environment. Syntax, pinned revisions and patch application are checked; a full build from a fresh clone of this publication has not yet been completed. Budget several hundred GB of free SSD space. The build wrapper caps Android work at one compile job, two CPUs (0–1), 10 GiB RAM and 12 GiB total including swap. Actual host swap must exist for that allowance to help. These limits also apply to nested kernel make commands in the reduced graph.

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

The three source forks already contain our device and kernel changes. `prepare-source.py` verifies their revisions and applies only the seven remaining platform patches; it also stages hash-verified GPU donors, isolates the legacy C2D dependency and regenerates vendor makefiles. Never apply the historical device/kernel patches on top again.

The build limits are fixed in `rom-build/build-rom.sh`; the former `BUILD_JOBS`, `BUILD_MEMORY`, `BUILD_MEMORY_SWAP`, and `GO_MEMORY_LIMIT` overrides are no longer used. Sync concurrency separately uses `SYNC_JOBS`. A shared lock in `build/records/host-build.lock` prevents overlapping Lenovo build/test jobs, and the wrapper refuses to start while a surviving Lenovo build container exists.

After normal Soong/Kati graph generation, `build-target-closure.py` exports the requested target's dependency graph, retains the exact reachable build rules, and independently verifies dependency equivalence before compiling with Siso's existing `out` state. Only nested kernel make concurrency is changed to one job; the original generated files remain untouched. Byte-identical regenerated vendor makefiles preserve their timestamps to avoid needless graph regeneration.

**Current limitation:** full Soong and Kati graph regeneration exceeded these limits on the development host. The correctness and compositor ROMs completed incremental builds using existing graphs after separate source/configuration audits. The reduced full-ROM dependency graph passed equivalence checks, but that does not establish that a fresh clone can generate its initial graphs with 10 GiB. There is no general stale-graph bypass in this public wrapper. Do not treat the development recovery procedure as permission to reuse graphs after arbitrary module or configuration changes. The resulting compositor ROM passed installed acceptance, including 94 file hashes and a short paired performance check; see compositor-results.md.

WebView is materialized from Git LFS and hash-checked before building. Outputs are under `build/lineage/out/target/product/tb128fu/`. The container base and package repositories are not frozen, so this is a pinned-source recipe, not a claim of bit-for-bit reproducibility.

Build output uses development signing defaults. The development upgrade verified OTA post-install and A/B switching with the existing development recovery. A public flashing procedure still requires the exact distributable recovery, clean-install and rollback validation. Google applications are a separate integration and are not bundled by these scripts.
