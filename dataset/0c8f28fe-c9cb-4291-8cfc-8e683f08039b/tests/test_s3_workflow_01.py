

import uuid
import pytest
from _s3_http import S3HTTPError as ClientError


def test_workflow_sync_then_mv(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    files = {
        "a.txt": b"alpha-content",
        "b.txt": b"beta-content",
        "nested/c.txt": b"gamma-content",
    }
    for rel, data in files.items():
        p = src_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    r = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r.returncode == 0

    listed = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {obj["Key"] for obj in listed}
    expected_keys = set(files.keys())
    assert expected_keys.issubset(keys)
    for rel, data in files.items():
        got = s3_client.get_object(Bucket=bucket, Key=rel)["Body"].read()
        assert got == data

    r = cli("s3", "mv", f"s3://{bucket}/a.txt", f"s3://{bucket}/moved/a.txt")
    assert r.returncode == 0

    with pytest.raises(ClientError) as exc:
        s3_client.head_object(Bucket=bucket, Key="a.txt")
    assert exc.value.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    moved = s3_client.get_object(Bucket=bucket, Key="moved/a.txt")["Body"].read()
    assert moved == files["a.txt"]

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
