import pytest
def test_cp_sse_kms_metadata_persisted_and_readable(cli, s3_client, tmp_path):
    bucket = 'stump-kms-35'
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / 'f.txt'
    src.write_bytes(b'payload-35')
    r = cli('s3', 'cp', str(src), f's3://{bucket}/k.txt', '--sse', 'aws:kms', '--sse-kms-key-id', 'foo')
    assert r.returncode == 0, f'cp with KMS must succeed, rc={r.returncode} stderr={r.stderr!r}'
    head = s3_client.head_object(Bucket=bucket, Key='k.txt')
    assert head.get('ServerSideEncryption') == 'aws:kms', f"SSE not set: {head.get('ServerSideEncryption')!r}"
    kms_id = head.get('SSEKMSKeyId', '')
    assert 'foo' in kms_id, f'KMSKeyId mismatch: {kms_id!r}'


def test_cp_overwrites_existing_object(cli, s3_client, tmp_path):
    bucket = 'stump-overwrite-39'
    s3_client.create_bucket(Bucket=bucket)
    p1 = tmp_path / 'v1.txt'
    p1.write_bytes(b'first')
    p2 = tmp_path / 'v2.txt'
    p2.write_bytes(b'second')
    r1 = cli('s3', 'cp', str(p1), f's3://{bucket}/k.txt')
    assert r1.returncode == 0
    r2 = cli('s3', 'cp', str(p2), f's3://{bucket}/k.txt')
    assert r2.returncode == 0
    body = s3_client.get_object(Bucket=bucket, Key='k.txt')['Body'].read()
    assert body == b'second', f'overwrite failed, got {body!r}'
