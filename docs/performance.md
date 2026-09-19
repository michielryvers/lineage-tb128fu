# Performance capture

See [measured CPU policy and results](performance-results.md) for the September 19 investigation.

Establish a baseline on the installed ROM before changing drivers, scheduler or
power settings. These tools collect evidence; they do not tune the device.

Use an explicit transport from `adb devices -l`. Prefer USB if actually present.
The capture works with non-root ADB on the development LineageOS 24 installation.
Pass `--adb /absolute/path/to/adb` if platform-tools is elsewhere.

```sh
python3 rom-build/capture-performance.py --serial DEVICE \
  --output diagnostics/observation-NEW
```

The default observes the current workload for 25 seconds without sending input.
Use `--duration-seconds 75` for a longer sequence; accepted durations are 10–180
seconds, and scripted scrolling requires at least 25. The exact duration is
saved in the configuration and metadata. Validate full event coverage and buffer
overruns for longer captures before trusting their timing distributions.
Record the workload separately. Every run needs a new private output directory.
The tool saves the exact Perfetto configuration, fingerprint, boot ID, renderer
property, charging/thermal/memory state, trace, command results and crash buffer.
It sends the configuration on stdin because the perfetto SELinux domain cannot
read shell-created configuration files under `/data/local/tmp` on this build.
Only the capture's unique device-side trace file is removed afterward.

For the native control, open Settings' **All apps**, verify portrait orientation
and native 1200×2000 resolution, and warm up with two pairs of opposing swipes.

```sh
python3 rom-build/capture-performance.py --serial DEVICE --settings-scroll \
  --output diagnostics/settings-NEW
```

This sends ten alternating vertical swipes at x=600 between y=1600 and y=600,
600 ms each with 600 ms pauses. The foreground app must be unlocked and awake.
Do not touch the device during a capture. The tool checks focus before gestures;
it cannot prevent interference after that check. Reject runs where content,
orientation, charging state, activity, or user interaction changed unexpectedly.

`--scroll-package PACKAGE` uses the same gestures in another foreground app.
**Inspect the entire path first.** In particular, use an empty gap between Home
Assistant cards; do not drag over lights, sliders, climate or automation controls.
The script does not determine whether a path is safe. It does not launch apps,
change settings, enable root, or verify the target page title automatically.

The shell swipe helper injects synchronously and its delivered MOVE cadence can
change with device performance. It is not a matched-input harness for comparisons
between CPU policies; verify actual event counts/cadence or use controlled
asynchronous injection before claiming causal CPU or energy differences.

Repeat three times before drawing a conclusion. Keep renderer, content, app
version, charging, brightness, orientation, thermal state, and trace configuration
consistent. Warm the app first. Do not screen-record during timed captures.

## Analysis

The configuration includes task creation/rename and process exit events so that
processes launched during a capture can be identified after zygote specialization.
The initial September 18 baseline predates these three events; its cold-launch
process names can remain `zygote64`. Do not silently attribute such rows to an app.
Keep each capture's saved configuration and use the same version for comparisons.

Run SQL with an official Perfetto trace processor (the launcher can be invoked as
`python3 tools/trace_processor` if it is not executable):

```sh
python3 tools/trace_processor query -f rom-build/performance-summary.sql \
  diagnostics/settings-NEW/trace.pftrace
python3 tools/trace_processor query -f rom-build/performance-active-drags.sql \
  diagnostics/settings-NEW/trace.pftrace
python3 tools/trace_processor query -f rom-build/performance-settings-attribution.sql \
  diagnostics/settings-NEW/trace.pftrace
```

The summary separates processes/layers, FrameTimeline labels and presentation
intervals. Presentation timestamps come from the matching SurfaceFlinger display
frame, not the end of the app's rendering pipeline. Full-run intervals include
intentional gesture pauses. The active-drag query requires both presentation
endpoints to fall inside the same injected DOWN..UP interval; verify ten drags
are present for the intended app. Even an active finger does not guarantee every
vsync needs new content (for example when scrolling against a boundary).

The Settings attribution query matches vsync tokens to Choreographer and
RenderThread slices and intersects those slices with actual thread states. Its
CPU/sleep/runnable times describe those slices, not the entire app frame or an
exclusive cause of jank. The generic buffer-call summary spans all processes;
filter by process/track before assigning those durations to a particular app.

Check trace errors and data loss, expected app/layer coverage, scheduling,
frequency, GPU busy events and memory-pressure counters before attribution.
A registered trace source can still emit no usable samples. GPU busy samples are
coarse whole-device counters, not per-frame or per-app GPU time. CPU frequency
maxima prove clocks were reached, not that they were adequate at each deadline.

Buffer Stuffing describes queued-buffer latency and can occur with smooth
presentation. Do not count every such label as a dropped frame. Never invert app
pipeline duration to report FPS. SurfaceView/video/browser trace coverage must
be checked independently; app UI timelines do not establish decoded video cadence.
See the [FrameTimeline documentation](https://perfetto.dev/docs/data-sources/frametimeline).

Charging battery-current readings are net battery flow, not total tablet power.
Short captures do not establish battery drain, suspend stability, or sustained
thermal performance. Keep raw traces, screenshots, private addresses and account
information local under ignored `diagnostics/`.
