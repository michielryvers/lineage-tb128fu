# Source provenance

The complete Android source set is recorded in `manifests/pinned.xml`; fork parent/base/revision information is in `provenance/forks.json`. Existing copyright and commit authorship are retained.

- Lenovo device/common/kernel bases: [Roynas-Android-Playground](https://github.com/Roynas-Android-Playground).
- Maintained kernel merge: [LineageOS Motorola SM6225](https://github.com/LineageOS/android_kernel_motorola_sm6225), commit `39bcecd5c63df849923b1faadc9cde482648a1a1`.
- ARM32 Adreno 615.76 donor: [galaxy-a05s/android_vendor_samsung_bengal_f](https://github.com/galaxy-a05s/android_vendor_samsung_bengal_f), commit `84a0df45a234684e8d7ce258b5c140f88fa50228`.
- ARM64 Adreno 615.98 donor: [SM6225-Android-Playground/proprietary_vendor_xiaomi_tapas](https://github.com/SM6225-Android-Playground/proprietary_vendor_xiaomi_tapas), commit `a17e3e16cfdd8a7cc04dd605b3105053cf0b5728`.

The four driver manifests record source URLs, hashes and sizes. `fetch-drivers.py` downloads and verifies those external files; this repository contains metadata, not the driver binaries. These proprietary components are separate from the open source kernel. The source manifest also references the original Lenovo vendor repositories instead of republishing them here.

Device-specific changes cover modern Android configuration, legacy vendor compatibility, snapshot/recovery setup, C2D dependency isolation, and the OpenGL UI default. Kernel changes include the maintained SM6225 merge, Lenovo wake IPC preservation, UART vote ownership, Wi-Fi bounds/CSA handling, gesture read EOF, FCM configuration and EROFS support. Platform patches remain small reviewable files under `rom-build/patches/`.

Private development diagnostics, recovery authorization keys, device backups, signing private keys, accounts and home-network configuration are intentionally absent.
