"""S3 client for MinIO server.

Uses the MinIO Python SDK internally but exposes a boto3-shaped API
(create_bucket, get_object, list_objects_v2, ...) so existing test
assertions on shapes like `["Buckets"]`, `["Body"].read()`, and
`["Contents"][i]["Key"]` keep working.
"""

from __future__ import annotations

import io
from datetime import timezone
from urllib.parse import urlparse

from minio import Minio
from minio.commonconfig import CopySource as _MinioCopySource
from minio.error import S3Error


class S3HTTPError(Exception):
    def __init__(self, code: str, message: str, status: int, operation: str = ""):
        super().__init__(
            f"An error occurred ({code}) when calling the {operation} operation: {message}"
        )
        self.response = {
            "Error": {"Code": code, "Message": message},
            "ResponseMetadata": {"HTTPStatusCode": status},
        }
        self.operation_name = operation


ClientError = S3HTTPError


class _Exceptions:
    """Namespace exposed as `s3_client.exceptions.ClientError`."""

    ClientError = S3HTTPError
    NoSuchBucket = S3HTTPError
    NoSuchKey = S3HTTPError


class _Body:
    """boto3.get_object()['Body'] stand-in; supports .read() and .close()."""

    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self, amt: int = -1) -> bytes:
        if amt is None or amt < 0:
            chunk = self._data[self._pos:]
            self._pos = len(self._data)
            return chunk
        chunk = self._data[self._pos:self._pos + amt]
        self._pos += len(chunk)
        return chunk

    def close(self) -> None:
        self._data = b""


def _translate(op: str, exc: S3Error) -> S3HTTPError:
    status = getattr(getattr(exc, "response", None), "status", 0) or 0
    return S3HTTPError(exc.code or "S3Error", exc.message or "", status, op)


def _iso(dt) -> str:
    if dt is None or dt == "":
        return ""
    if isinstance(dt, str):
        return dt
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _ci_get(mapping, key):
    key_lower = key.lower()
    for k, v in mapping.items():
        if k.lower() == key_lower:
            return v
    return None


class S3Client:
    def __init__(
        self,
        endpoint_url: str,
        region_name: str = "us-east-1",
        access_key: str = "raidentest",
        secret_key: str = "raidentest",
    ):
        parsed = urlparse(endpoint_url)
        netloc = parsed.netloc or parsed.path
        self._client = Minio(
            netloc,
            access_key=access_key,
            secret_key=secret_key,
            secure=parsed.scheme == "https",
            region=region_name,
        )
        self.endpoint = endpoint_url.rstrip("/")
        self.region = region_name
        self.exceptions = _Exceptions()

    def create_bucket(self, Bucket: str, **_) -> dict:
        try:
            self._client.make_bucket(Bucket, location=self.region)
        except S3Error as e:
            raise _translate("CreateBucket", e) from None
        return {"Location": f"/{Bucket}", "ResponseMetadata": {"HTTPStatusCode": 200}}

    def delete_bucket(self, Bucket: str, **_) -> dict:
        try:
            self._client.remove_bucket(Bucket)
        except S3Error as e:
            raise _translate("DeleteBucket", e) from None
        return {"ResponseMetadata": {"HTTPStatusCode": 204}}

    def head_bucket(self, Bucket: str, **_) -> dict:
        try:
            exists = self._client.bucket_exists(Bucket)
        except S3Error as e:
            raise _translate("HeadBucket", e) from None
        if not exists:
            raise S3HTTPError(
                "NoSuchBucket",
                "The specified bucket does not exist",
                404,
                "HeadBucket",
            )
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def list_buckets(self, **_) -> dict:
        try:
            buckets = self._client.list_buckets()
        except S3Error as e:
            raise _translate("ListBuckets", e) from None
        return {
            "Buckets": [
                {"Name": b.name, "CreationDate": _iso(b.creation_date)}
                for b in buckets
            ],
            "Owner": {},
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }

    def get_bucket_location(self, Bucket: str, **_) -> dict:
        try:
            exists = self._client.bucket_exists(Bucket)
        except S3Error as e:
            raise _translate("GetBucketLocation", e) from None
        if not exists:
            raise S3HTTPError(
                "NoSuchBucket",
                "The specified bucket does not exist",
                404,
                "GetBucketLocation",
            )
        return {
            "LocationConstraint": None if self.region == "us-east-1" else self.region,
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }

    def put_object(self, Bucket: str, Key: str, Body=b"", Metadata=None, **kwargs) -> dict:
        if isinstance(Body, str):
            Body = Body.encode()
        elif Body is None:
            Body = b""
        if isinstance(Body, (bytes, bytearray)):
            data = io.BytesIO(bytes(Body))
            length = len(Body)
        else:
            data = Body
            length = kwargs.get("ContentLength", -1)
        meta = {}
        for k, v in (Metadata or {}).items():
            meta[f"X-Amz-Meta-{k}"] = str(v)
        _kw_to_header = (
            ("CacheControl", "Cache-Control"),
            ("ContentDisposition", "Content-Disposition"),
            ("ContentLanguage", "Content-Language"),
            ("ContentEncoding", "Content-Encoding"),
            ("StorageClass", "x-amz-storage-class"),
            ("WebsiteRedirectLocation", "x-amz-website-redirect-location"),
            ("SSEKMSKeyId", "x-amz-server-side-encryption-aws-kms-key-id"),
        )
        for _kwarg, _header in _kw_to_header:
            _val = kwargs.get(_kwarg)
            if _val is not None:
                meta[_header] = str(_val)
        _sse = kwargs.get("ServerSideEncryption")
        if _sse:
            meta["x-amz-server-side-encryption"] = str(_sse)
        content_type = kwargs.get("ContentType") or "application/octet-stream"
        try:
            result = self._client.put_object(
                Bucket,
                Key,
                data,
                length,
                content_type=content_type,
                metadata=meta or None,
            )
        except S3Error as e:
            raise _translate("PutObject", e) from None
        etag = result.etag or ""
        if etag and not etag.startswith('"'):
            etag = f'"{etag}"'
        return {"ETag": etag, "ResponseMetadata": {"HTTPStatusCode": 200}}

    def get_object(self, Bucket: str, Key: str, **_) -> dict:
        try:
            response = self._client.get_object(Bucket, Key)
        except S3Error as e:
            raise _translate("GetObject", e) from None
        try:
            data = response.read()
            raw_headers = getattr(response, "headers", {}) or {}
            headers = {k.lower(): v for k, v in raw_headers.items()}
        finally:
            response.close()
            response.release_conn()
        resp = {
            "ETag": headers.get("etag", ""),
            "ContentLength": int(headers.get("content-length", len(data)) or len(data)),
            "LastModified": headers.get("last-modified", ""),
            "Metadata": {
                k[len("x-amz-meta-"):]: v
                for k, v in headers.items()
                if k.startswith("x-amz-meta-")
            },
            "Body": _Body(data),
            "ResponseMetadata": {"HTTPStatusCode": 200, "HTTPHeaders": headers},
        }

        for _hdr, _key in (
            ("x-amz-storage-class", "StorageClass"),
            ("x-amz-server-side-encryption", "ServerSideEncryption"),
            ("x-amz-server-side-encryption-aws-kms-key-id", "SSEKMSKeyId"),
            ("x-amz-website-redirect-location", "WebsiteRedirectLocation"),
            ("cache-control", "CacheControl"),
            ("content-disposition", "ContentDisposition"),
            ("content-language", "ContentLanguage"),
            ("content-encoding", "ContentEncoding"),
        ):
            _val = headers.get(_hdr)
            if _val is not None:
                resp[_key] = _val
        return resp

    def head_object(self, Bucket: str, Key: str, **_) -> dict:
        try:
            obj = self._client.stat_object(Bucket, Key)
        except S3Error as e:
            raise _translate("HeadObject", e) from None
        raw_meta = obj.metadata or {}
        user_meta = {
            k[len("x-amz-meta-"):]: v
            for k, v in raw_meta.items()
            if k.lower().startswith("x-amz-meta-")
        }
        resp = {
            "ETag": obj.etag or "",
            "ContentLength": int(obj.size or 0),
            "LastModified": _iso(obj.last_modified),
            "ContentType": obj.content_type or "",
            "Metadata": user_meta,
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }
        for hdr, key in (
            ("x-amz-storage-class", "StorageClass"),
            ("x-amz-server-side-encryption", "ServerSideEncryption"),
            ("x-amz-server-side-encryption-aws-kms-key-id", "SSEKMSKeyId"),
            ("x-amz-website-redirect-location", "WebsiteRedirectLocation"),
            ("cache-control", "CacheControl"),
            ("content-disposition", "ContentDisposition"),
            ("content-language", "ContentLanguage"),
            ("content-encoding", "ContentEncoding"),
        ):
            val = _ci_get(raw_meta, hdr)
            if val is not None:
                resp[key] = val
        return resp

    def delete_object(self, Bucket: str, Key: str, **_) -> dict:
        try:
            self._client.remove_object(Bucket, Key)
        except S3Error as e:
            raise _translate("DeleteObject", e) from None
        return {"ResponseMetadata": {"HTTPStatusCode": 204}}

    def copy_object(self, Bucket: str, Key: str, CopySource=None, **_) -> dict:
        if isinstance(CopySource, dict):
            src_bucket = CopySource["Bucket"]
            src_key = CopySource["Key"]
        else:
            src_bucket, _, src_key = str(CopySource).lstrip("/").partition("/")
        try:
            result = self._client.copy_object(
                Bucket, Key, _MinioCopySource(src_bucket, src_key)
            )
        except S3Error as e:
            raise _translate("CopyObject", e) from None
        return {
            "CopyObjectResult": {"ETag": result.etag or ""},
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }

    def list_objects_v2(
        self,
        Bucket: str,
        Prefix=None,
        Delimiter=None,
        MaxKeys=None,
        ContinuationToken=None,
        StartAfter=None,
        **_,
    ) -> dict:
        kwargs = {"recursive": Delimiter is None}
        if Prefix is not None:
            kwargs["prefix"] = Prefix
        if StartAfter is not None:
            kwargs["start_after"] = StartAfter
        try:
            all_objs = list(self._client.list_objects(Bucket, **kwargs))
        except S3Error as e:
            raise _translate("ListObjectsV2", e) from None
        limit = MaxKeys if MaxKeys is not None else 1000
        limited = all_objs[:limit]
        is_truncated = len(all_objs) > limit
        contents = []
        common = []
        for o in limited:
            if o.is_dir:
                common.append({"Prefix": o.object_name})
            else:
                storage_class = (
                    _ci_get(o.metadata or {}, "x-amz-storage-class") or "STANDARD"
                )
                contents.append({
                    "Key": o.object_name,
                    "LastModified": _iso(o.last_modified),
                    "ETag": o.etag or "",
                    "Size": int(o.size or 0),
                    "StorageClass": storage_class,
                })
        resp = {
            "Name": Bucket,
            "Prefix": Prefix or "",
            "KeyCount": len(contents) + len(common),
            "MaxKeys": limit,
            "IsTruncated": is_truncated,
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }
        if contents:
            resp["Contents"] = contents
        if common:
            resp["CommonPrefixes"] = common
        return resp
