#!/usr/bin/env python3
"""Capture bounded Perfetto data through an explicit ADB transport (25 seconds by default).

Default: observe the current screen without input. --settings-scroll or
--scroll-package sends ten alternating portrait swipes (x=600, y=1600 to 600)
in an already-open app, after checking lock state and focus. Navigate, inspect
the full scroll path for interactive controls and warm up beforehand.
Never changes renderer, clocks, resolution, security, settings, or root state.
Captures contain private app/process information. Output must be a new directory.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid


ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--duration-seconds', type=int, default=25,
                        help='Bounded observation duration, 25 by default (10–180 seconds)')
    parser.add_argument('--adb', type=Path, default=ROOT / 'tools/platform-tools/adb')
    gestures = parser.add_mutually_exclusive_group()
    gestures.add_argument('--settings-scroll', action='store_true')
    gestures.add_argument('--scroll-package', help='Foreground app with a verified safe center scroll path')
    args = parser.parse_args()
    if not 10 <= args.duration_seconds <= 180:
        parser.error('Duration must be between 10 and 180 seconds')
    if (args.settings_scroll or args.scroll_package) and args.duration_seconds < 25:
        parser.error('Scrolling captures require at least 25 seconds')
    package = 'com.android.settings' if args.settings_scroll else args.scroll_package
    if package and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]*', package):
        parser.error('Invalid package name')
    adb = [str(args.adb), '-s', args.serial]

    def run(*command, timeout=30):
        return subprocess.run(adb + list(command), capture_output=True, timeout=timeout)

    ready = run('get-state')
    if ready.returncode or ready.stdout.strip() != b'device':
        parser.error('Selected ADB transport is unavailable')
    window = run('shell', 'dumpsys window')
    policy = run('shell', 'dumpsys window policy')
    power = run('shell', 'dumpsys power')
    if package:
        focus = [line for line in window.stdout.decode().splitlines() if 'mCurrentFocus=' in line]
        if (not focus or package + '/' not in focus[0]
                or b'showing=false' not in policy.stdout
                or b'mWakefulness=Awake' not in power.stdout):
            parser.error('Selected app must be foreground, awake and unlocked; no input sent')
        size = run('shell', 'wm size; dumpsys input | grep "Viewport INTERNAL"')
        if (b'Physical size: 1200x2000' not in size.stdout
                or b'Override size' in size.stdout
                or b'orientation=0,' not in size.stdout):
            parser.error('Swipe path requires native 1200x2000 portrait; no input sent')

    os.umask(0o077)
    args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    config = Path(__file__).with_name('performance-trace.pbtxt').read_bytes()
    config, substitutions = re.subn(rb'duration_ms:\s*\d+',
                                   f'duration_ms: {args.duration_seconds * 1000}'.encode(), config)
    if substitutions != 1:
        raise RuntimeError('Expected exactly one duration in the trace configuration')
    (args.output / 'config.pbtxt').write_bytes(config)
    meta = {'started_at': datetime.now(timezone.utc).isoformat(),
            'serial': args.serial, 'duration_seconds': args.duration_seconds,
            'settings_scroll': args.settings_scroll, 'scroll_package': package,
            'config_sha256': hashlib.sha256(config).hexdigest(), 'commands': {}}

    def save(name, command):
        result = run('shell', command)
        (args.output / (name + '.txt')).write_bytes(result.stdout + b'\n[stderr]\n' + result.stderr)
        meta['commands'][name] = {'command': command, 'exit_code': result.returncode}

    snapshot_commands = {
        'identity': 'id; uname -a; getenforce; getprop ro.build.fingerprint; '
                    'getprop debug.hwui.renderer; cat /proc/sys/kernel/random/boot_id; cat /proc/uptime',
        'battery': 'dumpsys battery',
        'thermal': 'dumpsys thermalservice',
        'memory': 'cat /proc/meminfo; cat /proc/vmstat',
        'display-settings': 'wm size; wm density; settings get global stay_on_while_plugged_in; '
                            'settings get system screen_brightness; settings get system screen_brightness_mode; '
                            'dumpsys window | grep -E "mCurrentFocus|mFocusedApp"',
    }
    for name, command in snapshot_commands.items():
        save('before-' + name, command)
    (args.output / 'before-window.txt').write_bytes(window.stdout)
    (args.output / 'before-policy.txt').write_bytes(policy.stdout)
    (args.output / 'before-power.txt').write_bytes(power.stdout)

    token = 'perf-' + uuid.uuid4().hex
    remote_trace = '/data/misc/perfetto-traces/' + token + '.pftrace'
    try:
        with (args.output / 'perfetto.log').open('wb') as log, (args.output / 'config.pbtxt').open('rb') as cfg:
            proc = subprocess.Popen(adb + ['shell', 'perfetto', '--txt', '-c', '-',
                                          '-o', remote_trace], stdin=cfg, stdout=log, stderr=log)
            try:
                if package:
                    time.sleep(3)
                    # Check again immediately before the first gesture.
                    check = run('shell', 'dumpsys window | grep mCurrentFocus')
                    if (package + '/').encode() not in check.stdout:
                        raise RuntimeError('Foreground changed; no gestures sent')
                    commands = []
                    for i in range(10):
                        y1, y2 = (1600, 600) if i % 2 == 0 else (600, 1600)
                        commands.append(f'input swipe 600 {y1} 600 {y2} 600; sleep 0.6')
                    meta['gestures'] = {'path': commands, 'host_start': time.time()}
                    result = run('shell', '; '.join(commands), timeout=30)
                    meta['gestures']['exit_code'] = result.returncode
                    meta['gestures']['host_end'] = time.time()
                    (args.output / 'gestures.log').write_bytes(result.stdout + result.stderr)
                meta['perfetto_exit_code'] = proc.wait(timeout=args.duration_seconds + 15)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
        result = run('pull', remote_trace, str(args.output / 'trace.pftrace'))
        (args.output / 'pull.log').write_bytes(result.stdout + result.stderr)
        if result.returncode or meta['perfetto_exit_code']:
            raise RuntimeError('Trace capture failed; inspect logs')
        for name, command in snapshot_commands.items():
            save('after-' + name, command)
        if package:
            save('after-app-gfxinfo', 'dumpsys gfxinfo ' + package + ' framestats')
        save('after-crashes', 'logcat -b crash -d -t 1000')
    finally:
        # Delete only this run's unique temporary files.
        run('shell', 'rm', '-f', remote_trace)
        meta['finished_at'] = datetime.now(timezone.utc).isoformat()
        (args.output / 'metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    print(f'Saved {args.output.resolve()}', flush=True)


if __name__ == '__main__':
    main()
