-- Per-layer labels: never interpret app timeline durations as frame intervals.
SELECT p.name AS process,a.layer_name,a.jank_type,a.present_type,COUNT(*) AS frames,
 ROUND(AVG(a.dur)/1e6,3) AS pipeline_mean_ms,
 ROUND(PERCENTILE(a.dur/1e6,95),3) AS pipeline_p95_ms
FROM actual_frame_timeline_slice a JOIN process p USING(upid)
GROUP BY 1,2,3,4;
-- Presentation timestamps come from matched SurfaceFlinger display frames.
-- All gaps retained, including intentional pauses between gestures.
WITH displayed AS (
 SELECT DISTINCT p.name AS process,a.layer_name,d.ts+d.dur AS present_ts
 FROM actual_frame_timeline_slice a JOIN process p USING(upid)
 JOIN actual_frame_timeline_slice d ON a.display_frame_token=d.display_frame_token
 JOIN process dp ON dp.upid=d.upid
 WHERE a.layer_name IS NOT NULL AND a.present_type IN ('On-time Present','Late Present','Early Present')
 AND dp.name='/system/bin/surfaceflinger' AND d.dur>0 AND d.present_type!='Dropped Frame'
), gaps AS (
 SELECT *, (present_ts-LAG(present_ts) OVER(PARTITION BY process,layer_name ORDER BY present_ts))/1e6 AS gap_ms
 FROM displayed
)
SELECT process,layer_name,COUNT(gap_ms) AS intervals,ROUND(PERCENTILE(gap_ms,50),3) AS p50_ms,
 ROUND(PERCENTILE(gap_ms,95),3) AS p95_ms,ROUND(MAX(gap_ms),3) AS max_ms,
 SUM(gap_ms BETWEEN 14 AND 19) AS gaps_14_19ms,SUM(gap_ms>25) AS gaps_over_25ms,
 SUM(gap_ms>50) AS gaps_over_50ms
FROM gaps GROUP BY 1,2;
SELECT ct.name,COUNT(*) AS samples,MIN(c.value) AS min_value,MAX(c.value) AS max_value,
 MAX(c.value)-MIN(c.value) AS span
FROM counter c JOIN counter_track ct ON ct.id=c.track_id
WHERE ct.name IN ('MemAvailable','gpufreq','psi.mem.some','psi.mem.full','psi.io.some','psi.io.full',
 'pgmajfault','pgscan_direct','pgsteal_direct','pswpin','pswpout','batt.current_ua','batt.power_mw')
GROUP BY ct.id;
SELECT ct.name,ct.cpu,MIN(c.value) AS min_khz,MAX(c.value) AS max_khz
FROM counter c JOIN cpu_counter_track ct ON ct.id=c.track_id
WHERE ct.name='cpufreq' GROUP BY ct.id;
SELECT name,COUNT(*) AS events FROM ftrace_event WHERE name GLOB '*reclaim*'
 OR name GLOB '*kswapd*' OR name GLOB '*throttl*' OR name GLOB '*gpu_fault*' GROUP BY name;
SELECT name,value,severity FROM stats WHERE value!=0 AND (severity!='info' OR name GLOB '*overrun*' OR name GLOB '*data_loss*');
