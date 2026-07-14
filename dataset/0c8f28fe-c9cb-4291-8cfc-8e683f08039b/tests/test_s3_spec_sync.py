def test_sync_idempotent_second_run_does_not_reupload(cli, s3_client, tmp_path):
    bucket = 'stump-sync-idem-36'
    s3_client.create_bucket(Bucket=bucket)
    (tmp_path / 'a.txt').write_bytes(b'alpha')
    (tmp_path / 'b.txt').write_bytes(b'beta')
    assert cli('s3', 'sync', str(tmp_path), f's3://{bucket}/').returncode == 0
    assert cli('s3', 'sync', str(tmp_path), f's3://{bucket}/').returncode == 0
    keys = {o['Key'] for o in s3_client.list_objects_v2(Bucket=bucket).get('Contents', [])}
    assert {'a.txt', 'b.txt'} <= keys
    assert s3_client.get_object(Bucket=bucket, Key='a.txt')['Body'].read() == b'alpha'
    assert s3_client.get_object(Bucket=bucket, Key='b.txt')['Body'].read() == b'beta'
