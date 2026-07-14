

def test_mv_with_metadata_directive_replace(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='key.txt', Body=b'hello world')

    result = cli('s3', 'mv', 's3://bucket/key.txt', 's3://bucket/key2.txt',
                 '--metadata-directive', 'REPLACE')

    assert result.returncode == 0, result.stderr

    resp = s3_client.list_objects_v2(Bucket='bucket')
    keys = [obj['Key'] for obj in resp.get('Contents', [])]
    assert 'key2.txt' in keys
    assert 'key.txt' not in keys

    got = s3_client.get_object(Bucket='bucket', Key='key2.txt')
    assert got['Body'].read() == b'hello world'
