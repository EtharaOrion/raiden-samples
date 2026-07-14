

def test_rm_deletes_object(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='key.txt', Body=b'hello')

    s3_client.head_object(Bucket='bucket', Key='key.txt')

    result = cli('s3', 'rm', 's3://bucket/key.txt')

    assert result.returncode == 0, result.stderr

    resp = s3_client.list_objects_v2(Bucket='bucket')
    assert 'Contents' not in resp or all(
        obj['Key'] != 'key.txt' for obj in resp.get('Contents', [])
    )
