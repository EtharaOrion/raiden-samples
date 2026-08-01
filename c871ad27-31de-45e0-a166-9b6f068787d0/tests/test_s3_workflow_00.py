

import pytest
from _s3_http import S3HTTPError as ClientError


def test_workflow_cp_roundtrip_then_mv_then_rb(cli, s3_client, tmp_path):
    bucket = "test-cp-mv-rb-bucket"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "source.bin"
    payload = b"hello world\x00\x01\x02 round-trip data"
    src.write_bytes(payload)

    r = cli("s3", "cp", str(src), f"s3://{bucket}/dir/source.bin")
    assert r.returncode == 0

    obj = s3_client.get_object(Bucket=bucket, Key="dir/source.bin")
    assert obj["Body"].read() == payload

    dl = tmp_path / "downloaded.bin"
    r = cli("s3", "cp", f"s3://{bucket}/dir/source.bin", str(dl))
    assert r.returncode == 0
    assert dl.read_bytes() == payload

    r = cli("s3", "mv", f"s3://{bucket}/dir/source.bin", f"s3://{bucket}/dir/moved.bin")
    assert r.returncode == 0

    with pytest.raises(ClientError) as exc:
        s3_client.head_object(Bucket=bucket, Key="dir/source.bin")
    assert exc.value.response["Error"]["Code"] in ("404", "NoSuchKey")

    moved = s3_client.get_object(Bucket=bucket, Key="dir/moved.bin")
    assert moved["Body"].read() == payload

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode != 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets
