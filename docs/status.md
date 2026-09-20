# Validation status

Updated September 20, 2026. Evidence comes from one Qualcomm TB128FU development tablet; short tests do not establish long-term reliability.

The complete integrated development ROM built successfully and upgraded the existing installation to LineageOS 24 / Android 17, build `24.0-20260919-UNOFFICIAL-tb128fu`. The public device/kernel trees were checked for exact equality against the ordered patches used in that build. This is not yet a fresh-clone build of the public recipe or a clean-install test.

| Area | Evidence / remaining work |
| --- | --- |
| Upgrade | Signature-verified recovery OTA completed; target slot A marked itself successful and snapshots merged naturally; no data wipe |
| Installed contents | 94 installed hashes and the running kernel configuration match the verified artifacts; existing third-party package UIDs and account counts preserved |
| Compositor | Main thread alone on cores 4–7 after boot; RenderEngine remains 0–3. Post-flash Overview p95 33.385→25.054 ms; no app-return regression in the short screen. See [details](compositor-results.md) |
| CPU | Task/group UCLAMP and 36% top-app event policy; live touch boost reached 36% / 1.344 GHz minimum, then released to 0% / 300 MHz |
| Bluetooth | Headphone audio passed on the preceding build; new build service is on with zero crashes; audible headphone check not repeated |
| Media | New build hardware encoder produced all 30 synthetic test frames without restarting the media service; video playback was exercised on the preceding build, not repeated in this installation check |
| UI | Home Assistant, YouTube and Firefox launch/focus checks passed; mixed-app processes remained stable |
| Rendering | Skia OpenGL remains default; ARM32/64 direct Qualcomm GLES pixel tests pass as ordinary shell under enforcing SELinux |
| C2D | ARM32/64 C2D/GLES coexistence tests pass in root diagnostic domain; actual codec service remains in its normal enforcing domain |
| Vulkan | Earlier YouTube timeline black rectangles remain unresolved; no unvalidated HWUI retention patch or replacement driver included |
| Google apps | Exact separate GApps package reapplied after snapshot merge; 37 files verified, privileged Play services and active Google system APEX confirmed |
| Memory / suspend | Original VM/PPR policy retained; short sleep/wake placement check passed; extended idle and overnight tests remain outstanding |
| Security | SELinux enforcing; normal non-root ADB restored; not a security certification or complete vendor firmware update |

The final boot crash buffer was empty through the focused checks. The same 37-file Google package, privileged Play services and Google APEX were verified after the required separate restoration. The compositor correctness check sampled thread placement during screen recording, not only after it.

The existing authenticated development recovery was retained. No public recovery image or ROM binary is published here. Clean installation, rollback, fresh-clone recipe execution, extended battery behavior and broader mixed-app performance testing remain open. See [CPU evidence](performance-results.md) and the [release checklist](releases.md).
