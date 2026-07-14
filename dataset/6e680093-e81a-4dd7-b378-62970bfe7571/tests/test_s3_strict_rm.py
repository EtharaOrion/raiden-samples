def test_rm_request_payer_bare_flag_v2(cli, s3_client):
    bucket = 'rm-rp-v2-46a'
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key='key', Body=b'x')
    r = cli('s3', 'rm', f's3://{bucket}/key', '--request-payer')
    assert r.returncode == 0
    objs = s3_client.list_objects_v2(Bucket=bucket).get('Contents', [])
    assert all((o['Key'] != 'key' for o in objs))


def test_rm_request_payer_bare_flag_v3(cli, s3_client):
    bucket = 'rm-rp-v3-46b'
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key='a/b/c.txt', Body=b'x')
    r = cli('s3', 'rm', f's3://{bucket}/a/b/c.txt', '--request-payer')
    assert r.returncode == 0
    objs = s3_client.list_objects_v2(Bucket=bucket).get('Contents', [])
    assert all((o['Key'] != 'a/b/c.txt' for o in objs))
