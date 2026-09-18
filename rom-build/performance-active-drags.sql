-- Presentation intervals only while the target receives injected finger drags.
-- Both endpoints must lie within the same DOWN..UP window (no inter-gesture pauses).
CREATE PERFETTO TABLE drag_events AS
SELECT p.upid,p.name AS process,s.ts,s.name,
 LEAD(s.ts) OVER (PARTITION BY p.upid ORDER BY s.ts) AS next_ts,
 LEAD(s.name) OVER (PARTITION BY p.upid ORDER BY s.ts) AS next_name
FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid)
WHERE t.is_main_thread AND (s.name GLOB 'dispatchInputEvent MotionEvent DOWN deviceId=-1*'
 OR s.name GLOB 'dispatchInputEvent MotionEvent UP deviceId=-1*');
CREATE PERFETTO TABLE drags AS
SELECT * FROM drag_events WHERE name GLOB '* DOWN *' AND next_name GLOB '* UP *';
SELECT process,COUNT(*) AS drags,ROUND(SUM(next_ts-ts)/1e9,3) AS touch_seconds FROM drags GROUP BY process;
WITH presented AS (
 SELECT DISTINCT p.upid,p.name AS process,a.layer_name,d.ts+d.dur AS present_ts
 FROM actual_frame_timeline_slice a JOIN process p USING(upid)
 JOIN actual_frame_timeline_slice d ON a.display_frame_token=d.display_frame_token
 JOIN process dp ON dp.upid=d.upid
 WHERE a.layer_name IS NOT NULL AND a.present_type IN ('On-time Present','Late Present','Early Present')
 AND dp.name='/system/bin/surfaceflinger' AND d.dur>0 AND d.present_type!='Dropped Frame'
), gaps AS (
 SELECT *,LAG(present_ts) OVER(PARTITION BY upid,layer_name ORDER BY present_ts) AS previous_ts FROM presented
), active AS (
 SELECT g.*,(present_ts-previous_ts)/1e6 AS gap_ms FROM gaps g
 WHERE EXISTS (SELECT 1 FROM drags w WHERE w.upid=g.upid AND g.previous_ts>=w.ts AND g.present_ts<=w.next_ts)
)
SELECT process,layer_name,COUNT(*) AS active_intervals,ROUND(PERCENTILE(gap_ms,50),3) AS p50_ms,
 ROUND(PERCENTILE(gap_ms,95),3) AS p95_ms,ROUND(PERCENTILE(gap_ms,99),3) AS p99_ms,
 ROUND(MAX(gap_ms),3) AS max_ms,SUM(gap_ms>25) AS over25ms FROM active GROUP BY 1,2;
