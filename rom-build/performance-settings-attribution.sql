WITH work AS (
 SELECT a.surface_frame_token AS token,a.jank_type,t.utid,t.name AS thread,s.ts,s.dur
 FROM actual_frame_timeline_slice a JOIN process p USING(upid)
 JOIN thread t ON t.upid=p.upid JOIN thread_track tt USING(utid)
 JOIN slice s ON s.track_id=tt.id AND (s.name='Choreographer#doFrame '||a.surface_frame_token
 OR s.name='DrawFrames '||a.surface_frame_token)
 WHERE p.name='com.android.settings' AND a.jank_type GLOB '*App Deadline*'
)
SELECT w.token,w.thread,w.jank_type,ROUND(w.dur/1e6,3) AS elapsed_ms,st.state,
 ROUND(SUM(MIN(st.ts+st.dur,w.ts+w.dur)-MAX(st.ts,w.ts))/1e6,3) AS state_ms
FROM work w JOIN thread_state st ON st.utid=w.utid AND st.dur>0 AND st.ts<w.ts+w.dur AND st.ts+st.dur>w.ts
GROUP BY w.token,w.thread,st.state ORDER BY w.token,w.thread;
SELECT ROUND(100.0*SUM(EXTRACT_ARG(arg_set_id,'busy'))/SUM(EXTRACT_ARG(arg_set_id,'elapsed')),2) AS gpu_busy_percent,
 COUNT(*) AS gpu_samples FROM ftrace_event WHERE name='kgsl_gpubusy';
SELECT name,COUNT(*) AS count,ROUND(AVG(dur)/1e6,3) AS mean_ms,ROUND(PERCENTILE(dur/1e6,95),3) AS p95_ms,
 ROUND(MAX(dur)/1e6,3) AS max_ms FROM slice WHERE name IN ('dequeueBuffer','queueBuffer','eglSwapBuffersWithDamageKHR','syncFrameState') GROUP BY name;
