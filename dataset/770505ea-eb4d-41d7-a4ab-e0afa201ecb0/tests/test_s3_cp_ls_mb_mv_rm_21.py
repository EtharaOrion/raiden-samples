

def test_rm_with_request_payer_deletes_object(cli, s3_client):
    s3_client.create_bucket(Bucket='mybucket')
    s3_client.put_object(Bucket='mybucket', Key='mykey', Body=b'hello')

    result = cli('s3', 'rm', 's3://mybucket/mykey', '--request-payer')

    assert result.returncode == 0

    response = s3_client.list_objects_v2(Bucket='mybucket')
    assert 'Contents' not in response or all(
        obj['Key'] != 'mykey' for obj in response.get('Contents', [])
    )
