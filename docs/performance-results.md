# Measured CPU policy — September 19, 2026

The integrated development ROM enables `CONFIG_UCLAMP_TASK` and `CONFIG_UCLAMP_TASK_GROUP`, replacing mutually exclusive `CONFIG_SCHED_TUNE`. The Power HAL requests a 36% minimum utilization clamp for the top-app group during INTERACTION and a 750 ms LAUNCH node request. The clamp resets to zero after hints release. This influences scheduling and frequency selection; it does not pin applications to the performance cores.

The policy retains the original 1.344 GHz interaction frequency floor, clock maxima and interaction lifetime. Schedutil nodes initialize to the observed screen-on defaults: little up/down 2/20 ms and big up/down 0.5/10 ms. Original VM/PPR settings remain unchanged. The unvalidated HWUI context-retention experiment is excluded.

## Matched-input Settings comparison

Six accepted 25-second captures used A–B–C–C–B–A order on the same UCLAMP kernel. A used original hints; B added the 36% clamp with a 1.7664 GHz floor; C used the clamp with the original 1.344 GHz floor. Fixed-rate asynchronous injection produced 852 MOVE events per condition. Input count/jitter, drag coverage, trace import/overwrite and crash checks passed. Values below aggregate each pair of captures.

| Measure | A: original hints | B: higher floor | C: selected policy |
| --- | ---: | ---: | ---: |
| Settings main-thread execution during drag windows | 2931.3 ms | 1418.9 ms | 1405.8 ms |
| Main-thread execution on big cores | 11.26% | 98.17% | 98.37% |
| Presentation intervals within 33.5 ms | 366/368 | 388/388 | 384/384 |
| Intervals above 50 ms | 0 | 0 | 0 |
| Cluster crossings per 12 drags | 119 | 14 | 12 |
| Median DOWN to first big-core main-thread execution | 56.743 ms* | 7.411 ms | 7.763 ms |

*Original hints used a big core in 11 of 12 drags; the median excludes the remaining drag.

C reduced main-thread execution time by 52.04% in this workload. Raising the floor further added no measured benefit, so C met the preselected lowest-floor rule. Actual execution can still reach the normal 2.4 GHz maximum. Boost release remained approximately 0.7–0.9 seconds after finger-up. These are scheduling observations, not end-to-end input latency or proof of deep idle. A already met the small cadence screen, so this is not evidence that all everyday stutters are fixed.

## Energy screening and limits

Four matched-input A–C–C–A runs lasted approximately 215 seconds each with charging input suspended. Battery energy estimated from BMS current/voltage was 278.23/269.69 J for A and 269.01/264.25 J for C: means 273.96 versus 266.63 J, a 2.68% reduction. Whole-system CPU busy time fell 18.75%; frame count differed by −0.28%; HWUI jank counts were 118/5798 versus 47/5782. The 738 battery samples and 160 gestures passed coverage checks; battery temperature was 26.2–26.7°C.

This is a small screen-on result on one device, with both policies using the same UCLAMP kernel. It does not establish all-day battery life, deep-sleep behavior or the complete new-kernel-versus-original-ROM energy difference. Earlier fresh-boot mixed-app trials did not consistently meet the broader app-switching and reclaim goals. Those goals remain incomplete.

The integrated September 19 ROM passed a functional touch boost/release check, plus focused graphics/media and app checks; it has not repeated the full quantitative mixed-app comparison or extended battery/stability testing.

A fixed Firefox toolbar was a separately adopted app preference, with a favorable earlier scrolling comparison; it is not a ROM patch. Standard profile-guided ART compilation was exercised, but no isolated speedup was established. Rejected VM changes, freezer disabling, compaction backports and extra clock increases are not included.

## Measurement caveat

The generic capture tool's `adb shell input swipe` is useful for observation but does not provide matched delivered event rates across CPU policies. Its synchronous injection cadence changed between roughly 30 and 60 Hz in earlier tests. The results above use a separate fixed-rate asynchronous harness with verified counts and jitter; they must not be attributed to the generic published swipe helper. Raw traces, screenshots and device/account details remain local.
