"""This proxy's fixed, allowlisted upstream and native request shape.

Inventoried from Earth Platform 0.1.0-alpha.73 (tag combined-73 / commit
88b13c33954550c6ac660dceb743a4288a9aafac),
geography/src/main/java/io/earthplatform/geography/globe/HrdemElevation.java:
the mod reads one cloud-optimised GeoTIFF per 500 km square from Natural
Resources Canada's public S3 bucket -- only the bare-earth "dtm" product,
never "dsm". Each file is 1-10 GB; the mod never does a whole-file GET, only
byte-range header/block reads. Live checks against the bucket below confirm
Accept-Ranges: bytes, 206 Partial Content with a correct Content-Range, and
416 on an out-of-bounds range. The ETag is a multipart-upload ETag (not a
content hash) because of file size, but is still a valid, stable revision
token.
"""
import re

from range_cache_proxy import SourceConfig

_PATH_RE = re.compile(r"^/(\d+_\d+)-mosaic-2m-dtm\.tif$")


def _validate_path(path: str):
    return path.lstrip("/") if _PATH_RE.match(path) else None


SOURCE = SourceConfig(
    name="hrdem",
    dataset_id="hrdem-2m-v1",
    default_upstream="https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-mosaic-2m/",
    upstream_env_var="HRDEM_CACHE_UPSTREAM",
    validate_path=_validate_path,
    probe_path="/10_2-mosaic-2m-dtm.tif",
)
