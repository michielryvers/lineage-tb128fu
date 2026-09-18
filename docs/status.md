# Validation status

Initial source export: 2026-09-18. Evidence comes from one Qualcomm TB128FU development tablet; passing a short manual test does not establish long-term reliability.

| Area | Evidence / remaining work |
| --- | --- |
| Android | LineageOS 24 / Android 17 development build reached setup, lock screen and apps |
| Bluetooth | Headphones paired and played audio successfully after UART fixes |
| Video | YouTube playback worked |
| UI rendering | OpenGL corrected missing/flickering elements in manual testing; it is the default |
| Vulkan | Black boxes persist during YouTube timeline scrubbing; partial-redraw changes did not resolve it |
| GPU stack | Experimental 615.98 ARM64 / 615.76 ARM32 donors with private legacy GSL for C2D; more compatibility coverage needed |
| Google apps | Core services were exercised on the development installation; a full GApps distribution is not part of this source recipe |
| Memory / suspend | Gesture-read EOF and serial vote fixes included; extended idle, overnight and suspend/resume stress testing still needed |
| Recovery / OTA | Init and update-engine snapshot fixes included; previous attempts had mount/post-install failures; final combined OTA remains unvalidated |
| Security | Development testing used SELinux enforcing; this is not a security certification or complete vendor firmware update |

There is no public release artifact. Do not infer release readiness from a successful source or metadata check.
