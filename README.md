# hrdem-cache-proxy

One of four independently configurable/deployable byte-range caching proxies
for MINECRAFT-577 (Build S3 range-cache proxies for regional elevation
refiners, shared delivery Story MINECRAFT-571). This repo covers Canada
HRDEM 2m only; USGS 3DEP, Antarctica REMA and Copernicus DEM 30m are each
their own separate repo/service, sharing only the `range_cache_proxy.py`
cache core (vendored, not a runtime dependency between them).

Pinned source: Earth Platform `combined-73` (= release 0.1.0-alpha.73,
commit `88b13c33954550c6ac660dceb743a4288a9aafac`),
`geography/src/main/java/io/earthplatform/geography/globe/HrdemElevation.java`.

## Upstream contract

- Fixed, allowlisted upstream:
  `https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-mosaic-2m/`
  (the exact default from `HrdemElevation.AWS_HRDEM`; override via
  `HRDEM_CACHE_UPSTREAM`, default untouched when unset).
- Path: `{square}-mosaic-2m-dtm.tif`, one cloud-optimised GeoTIFF per
  500 km square -- the bare-earth "dtm" product only; the mod never reads
  the "dsm" product.
- Each file is 1-10 GB; the mod never does a whole-file GET, only
  byte-range header/block reads via `FloatCogs`. This proxy caches at that
  same granularity.
- Verified live against the real bucket (anonymous, read-only,
  no-sign-request): `Accept-Ranges: bytes`, 206 with a correct
  `Content-Range`, 416 on an out-of-bounds range. The ETag is a
  multipart-upload ETag (not a content hash, given file size) but is still
  a valid, stable revision token.
- Attribution: "Canada: High Resolution Digital Elevation Model (HRDEM),
  Natural Resources Canada; contains information licensed under the Open
  Government Licence - Canada" (`HrdemElevation.ATTRIBUTION`). OGL-Canada
  explicitly permits copying/caching/republishing with attribution; no
  restriction found.

## Contract this proxy keeps

- Loopback-only bind (`127.0.0.1`).
- Request path validated against the exact `{square}-mosaic-2m-dtm.tif`
  shape -- no arbitrary URL forwarding.
- SQLite cache keyed by `(path, byte-range)`, restart-persistent, bounded
  with LRU eviction.
- Concurrent misses for the same exact range single-flight to one upstream
  request.
- A transient upstream failure (5xx, connection error) is retried 3x with
  backoff and never cached; a truncated transfer is never cached; an
  upstream that answers 200 instead of 206 to a range request is never
  trusted or sliced as if it had honored the range.
- Genuine upstream 404/403/416 are passed through verbatim and never
  cached as success.
- Dedicated `/__health` probe: TTL 0, a fresh `Range: bytes=0-0` read of a
  real always-present object on every call, never served from the ordinary
  data cache -- so proxy-process liveness is distinguished from upstream
  reachability, and a fixture upstream outage is reflected without a direct
  bypass.
- `/__stats` reports cold/warm/upstream request and byte counters.

## Run

```
python3 -m unittest test_proxy -v   # 17 tests, local mock upstream only
python3 proxy.py                     # serves on 127.0.0.1:8102 by default
```

## Status

No live-provider traffic beyond the read-only verification probes recorded
on MINECRAFT-577; no merge/release/Zippy action. Tested against a local mock
upstream only. Mod-side wiring is tracked on MINECRAFT-580, the coordinated
alpha.73 integration lane -- not duplicated here.
