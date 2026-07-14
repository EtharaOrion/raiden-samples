

def test_sync_from_nonexistent_directory_fails(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.create_bucket(Bucket='decoy-bucket-do-not-touch')
    missing_dir = str(tmp_path / 'does-not-exist-dir')

    result = cli('s3', 'sync', missing_dir, 's3://bucket/')

    assert result.returncode != 0

    resp = s3_client.list_objects_v2(Bucket='bucket')
    assert resp.get('KeyCount', 0) == 0
    buckets = {b['Name'] for b in s3_client.list_buckets()['Buckets']}
    assert 'decoy-bucket-do-not-touch' in buckets
