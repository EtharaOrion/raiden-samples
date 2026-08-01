"""Stdlib-only raw-HTTP DynamoDB client for the verifier (DynamoDB JSON, v20120810).

No boto3 / botocore / moto — we speak the wire protocol directly over urllib.
Numbers travel as JSON strings ({"N": "5"}); helpers marshal to/from native Python.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

_TARGET_PREFIX = "DynamoDB_20120810"

# DynamoDB Local does not verify the SigV4 signature but wants a well-formed
# Authorization header; the signature value is ignored.
_AUTH = (
    "AWS4-HMAC-SHA256 "
    "Credential=dummy/20120810/us-east-1/dynamodb/aws4_request, "
    "SignedHeaders=content-type;host;x-amz-target, "
    "Signature=0000000000000000000000000000000000000000000000000000000000000000"
)


class DDBHTTPError(Exception):
    """boto-shaped: .response['Error']['Code'] carries the DynamoDB error code."""

    def __init__(self, code, message, status, operation=""):
        super().__init__(
            "An error occurred (%s) when calling the %s operation: %s"
            % (code, operation, message)
        )
        self.response = {
            "Error": {"Code": code, "Message": message},
            "ResponseMetadata": {"HTTPStatusCode": status},
        }
        self.operation_name = operation


ClientError = DDBHTTPError


def _num(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return repr(v) if isinstance(v, float) else str(v)


def _pynum(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def to_av(v):
    """Marshal a native Python value into a DynamoDB AttributeValue."""
    if v is None:
        return {"NULL": True}
    if isinstance(v, bool):
        return {"BOOL": v}
    if isinstance(v, (int, float)):
        return {"N": _num(v)}
    if isinstance(v, str):
        return {"S": v}
    if isinstance(v, (bytes, bytearray)):
        return {"B": base64.b64encode(bytes(v)).decode("ascii")}
    if isinstance(v, dict):
        return {"M": {k: to_av(x) for k, x in v.items()}}
    if isinstance(v, (list, tuple)):
        return {"L": [to_av(x) for x in v]}
    if isinstance(v, set):
        elems = list(v)
        if elems and all(isinstance(x, str) for x in elems):
            return {"SS": elems}
        if elems and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in elems):
            return {"NS": [_num(x) for x in elems]}
        if elems and all(isinstance(x, (bytes, bytearray)) for x in elems):
            return {"BS": [base64.b64encode(bytes(x)).decode("ascii") for x in elems]}
    raise TypeError("cannot marshal %r to a DynamoDB AttributeValue" % (type(v),))


def from_av(av):
    """Unmarshal a DynamoDB AttributeValue into a native Python value."""
    (tag, val), = av.items()
    if tag == "NULL":
        return None
    if tag == "BOOL":
        return val
    if tag == "N":
        return _pynum(val)
    if tag == "S":
        return val
    if tag == "B":
        return base64.b64decode(val)
    if tag == "M":
        return {k: from_av(x) for k, x in val.items()}
    if tag == "L":
        return [from_av(x) for x in val]
    if tag == "SS":
        return set(val)
    if tag == "NS":
        return {_pynum(x) for x in val}
    if tag == "BS":
        return {base64.b64decode(x) for x in val}
    raise ValueError("unknown AttributeValue tag %r" % (tag,))


def to_item(d):
    return {k: to_av(v) for k, v in d.items()}


def from_item(d):
    return {k: from_av(v) for k, v in (d or {}).items()}


class DDBClient:
    def __init__(self, endpoint_url=None, region_name="us-east-1"):
        endpoint_url = (
            endpoint_url
            or os.environ.get("AWS_ENDPOINT_URL_DYNAMODB")
            or os.environ.get("AWS_ENDPOINT_URL")
        )
        p = urlparse(endpoint_url)
        self.endpoint = ("%s://%s" % (p.scheme, p.netloc)) if p.scheme else ("http://%s" % endpoint_url)
        self.region = region_name

    def _request(self, operation, payload, timeout=5.0):
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/x-amz-json-1.0",
                "X-Amz-Target": "%s.%s" % (_TARGET_PREFIX, operation),
                "X-Amz-Date": "20120810T000000Z",
                "Authorization": _AUTH,
                "Host": urlparse(self.endpoint).netloc,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                doc = json.loads(raw)
            except Exception:
                doc = {}
            raw_type = doc.get("__type", "") or ""
            code = raw_type.split("#")[-1] if "#" in raw_type else (raw_type or "UnknownError")
            message = doc.get("message") or doc.get("Message") or ""
            raise DDBHTTPError(code, message, e.code, operation) from None

    def list_tables(self):
        return self._request("ListTables", {})

    def create_table(self, TableName, KeySchema, AttributeDefinitions,
                     BillingMode="PAY_PER_REQUEST", **extra):
        payload = {
            "TableName": TableName,
            "KeySchema": KeySchema,
            "AttributeDefinitions": AttributeDefinitions,
            "BillingMode": BillingMode,
        }
        payload.update(extra)
        return self._request("CreateTable", payload)

    def delete_table(self, TableName):
        return self._request("DeleteTable", {"TableName": TableName})

    def put_item(self, TableName, Item, **extra):
        payload = {"TableName": TableName, "Item": Item}
        payload.update(extra)
        return self._request("PutItem", payload)

    def get_item(self, TableName, Key, ConsistentRead=True, **extra):
        payload = {"TableName": TableName, "Key": Key, "ConsistentRead": ConsistentRead}
        payload.update(extra)
        return self._request("GetItem", payload)

    def update_item(self, TableName, Key, **extra):
        payload = {"TableName": TableName, "Key": Key}
        payload.update(extra)
        return self._request("UpdateItem", payload)

    def delete_item(self, TableName, Key, **extra):
        payload = {"TableName": TableName, "Key": Key}
        payload.update(extra)
        return self._request("DeleteItem", payload)

    def query(self, TableName, ConsistentRead=True, **extra):
        payload = {"TableName": TableName, "ConsistentRead": ConsistentRead}
        payload.update(extra)
        return self._request("Query", payload)

    def reset_all_tables(self):
        for name in self.list_tables().get("TableNames", []):
            try:
                self.delete_table(name)
            except DDBHTTPError as exc:
                if exc.response.get("Error", {}).get("Code", "") != "ResourceNotFoundException":
                    raise
