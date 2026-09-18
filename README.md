# Unofficial LineageOS 24 for Lenovo Tab M10 Plus (3rd Gen), TB128FU

Experimental Android 17 device-specific development for the **Qualcomm TB128FU**. This is an independent community project, not an official LineageOS or Lenovo release. Other model numbers, including the MediaTek TB125FU, are not supported by this work.

**Source publication only: there is no public installable ROM release yet.** The tablet has been tested using a full development build followed by incremental boot/vendor changes. The complete exported source set still needs a clean build and end-to-end installation test before a binary release.

## Repositories

| Repository | Purpose |
| --- | --- |
| [lineage-tb128fu](https://github.com/michielryvers/lineage-tb128fu) | Pinned Android manifest, build orchestration, platform patches, donor provenance and issue tracking |
| [android_device_lenovo_tb128fu](https://github.com/michielryvers/android_device_lenovo_tb128fu) | Product configuration and vendor extraction definitions |
| [android_device_lenovo_sm6225-common](https://github.com/michielryvers/android_device_lenovo_sm6225-common) | Shared board configuration, recovery, services and graphics compatibility |
| [android_kernel_lenovo_tb128fu](https://github.com/michielryvers/android_kernel_lenovo_tb128fu) | Lenovo kernel with maintained SM6225 changes and device fixes |

Source forks use `codex/lineage-24.0`. Original upstream history is retained. The manifest pins exact commits, including third-party vendor sources; it does not follow moving branch tips.

## Current state

Bluetooth headphone audio and YouTube playback have been exercised. Android UI rendering defaults to OpenGL because Vulkan still produces black rectangles while scrubbing YouTube videos. Long-running stability, a clean installation of the final combined source set, and upgrade/rollback testing remain open.

- [Build instructions](docs/build.md)
- [Tested behavior and known issues](docs/status.md)
- [Updating from upstream](docs/upstream.md)
- [Source and driver provenance](docs/provenance.md)
- [Release checklist](docs/releases.md)

Please file reproducible bugs here with the build revision, steps, and a **redacted** log excerpt. Do not upload account tokens, full personal bugreports, device backups or private keys.

## Licensing and credits

Existing source files and patches retain their upstream component licenses and notices. New orchestration scripts and documentation in this repository are available under Apache-2.0; see LICENSE. That grant does not cover externally fetched proprietary firmware, GPU libraries or Google applications. No proprietary binaries or GApps are committed here.

Thanks to Roynas-Android-Playground for the original Lenovo bring-up, LineageOS and AOSP, the LineageOS Motorola SM6225 maintainers, galaxy-a05s, and SM6225-Android-Playground. See the provenance documentation for exact sources and revisions.
