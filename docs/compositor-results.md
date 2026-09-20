# September 20 compositor and correctness follow-up

A bounded comparison found a benefit from placing only SurfaceFlinger's main thread on cores 4–7 after boot initialization. RenderEngine retains its original system-background cpuset on cores 0–3. Clock limits, the accepted 36% interaction clamp, thermal protection and render backend are unchanged.

| Overview active presentation intervals | Baseline A | Main-only B |
| --- | ---: | ---: |
| First pair p95 | 33.493 ms | 17.101 ms |
| Reverse-order confirmation p95 | 33.513 ms | 17.035 ms |

That is a 48.94% and 49.17% p95 reduction in this specific Overview gesture workload. The paired Settings, Firefox, YouTube and Home Assistant app-return means did not regress. Larger app-return gains in the initial screen were smaller on confirmation; no general app-speedup percentage is claimed. Short recordings used fixed-rate gestures and actual CPU-placement checks. No dedicated battery measurement was requested for this follow-up.

Moving the broader inherited SurfaceFlinger group had previously worsened important app returns and was rejected. RenderEngine-only placement did not provide a meaningful frame benefit and slowed app returns. Broader 0–7 critical-thread eligibility had no frame benefit and is not selected. The running power HAL reported no hint-session support, so an ADPF property toggle was not treated as an effective experiment. No supported, evidence-backed 60 Hz timing alternative was selected.

The production implementation applies an optional SFMainPostBootPolicy on the main scheduler only after boot workers and RenderEngine initialize. The device supplies the dedicated cpuset. The original early SFMainPolicy remains unchanged. Verify that no other thread enters this group after boot, app switching, virtual-display recording or sleep/wake. This does not claim that Linux disables cgroup inheritance for future children.

Two earlier correctness fixes are retained: upstream trace-marker stream semantics prevent a tracing-triggered native-zygote FD-offset failure; PowerStatsAggregator.reset preserves cached charging/screen attribution state, with a regression that fails before the fix and passes afterward. The kernel result is not an ordinary untraced launch-speed claim. The tablet has GNSS; the attribution fix does not prove that every historical GPS battery percentage was caused by this defect or erase old statistics.

The incremental development build completed 53 actions in 16m45s and reused 228,736 steps. Its 25 integrated patches were packaged and installed normally from slot B to A, with natural successful-boot marking and snapshot merge. The exact Google package was restored afterward. Installed verification passed 94 hashes, 37 Google files, existing package UIDs and account counts, enforcing SELinux, CPU boost/release, both GLES/C2D ABIs, 30 encoded frames, short sleep/wake and ordinary app launches. The final crash buffer was empty; non-root ADB and the user's night settings were restored.

The post-flash paired check measured Overview p95 **33.385 → 25.054 ms (24.95% lower)**. Intervals over 25 ms fell from 16/162 to 9/171, and intervals over 33.5 ms from 7 to 1; neither run had intervals over 50 ms. The four app-return means did not regress and app processes remained unchanged. This smaller p95 gain than the pre-flash pairs illustrates run-to-run variation and percentile sensitivity in a short screen. It is not evidence that all stutters are gone. Main-only placement was checked before, during and after virtual-display recording, after sleep/wake, and at final cleanup; RenderEngine stayed on 0–3.

Development OTA SHA256: `79da2c4870e69b09a1e515fee33109665f2c996e294a82b93aabcff8623e61f1`.
Installed SurfaceFlinger SHA256: `1be6a4009caaaf0ee11be9da63ed6a8c4bbfbe63f8f36301067411e1810ddba8`.
The displayed Lineage version remains `24.0-20260919-UNOFFICIAL-tb128fu`; use these hashes to distinguish this incremental artifact. No public binary release is provided.
