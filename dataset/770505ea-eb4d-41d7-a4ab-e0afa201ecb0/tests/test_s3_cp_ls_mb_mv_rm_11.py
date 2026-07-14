

def test_s3_ls_empty_bucket_returns_zero(cli, s3_client):
    s3_client.create_bucket(Bucket='target-empty-bucket')

    result = cli('s3', 'ls', 's3://target-empty-bucket')
    assert result.returncode == 0, f"expected 0, got {result.returncode}; stderr={result.stderr!r}"
    assert 'PRE ' not in result.stdout
    resp = s3_client.list_objects_v2(Bucket='target-empty-bucket')
    assert resp.get('KeyCount', 0) == 0
    assert 'Contents' not in resp

    result2 = cli('s3', 'ls')
    assert result2.returncode == 0, f"expected 0, got {result2.returncode}; stderr={result2.stderr!r}"
    assert 'target-empty-bucket' in result2.stdout, (
        f"CLI did not list bucket; stdout={result2.stdout!r}"
    )
