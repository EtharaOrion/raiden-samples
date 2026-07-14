

def test_rm_with_request_payer_deletes_object(cli, s3_client):
    s3_client.create_bucket(Bucket='mybucket')
    s3_client.put_object(Bucket='mybucket', Key='mykey', Body=b'hello')

    result = cli('s3', 'rm', 's3://mybucket/mykey', '--request-payer')

    assert result.returncode == 0, result.stderr

    resp = s3_client.list_objects_v2(Bucket='mybucket')
    keys = [obj['Key'] for obj in resp.get('Contents', [])]
    assert 'mykey' not in keys
