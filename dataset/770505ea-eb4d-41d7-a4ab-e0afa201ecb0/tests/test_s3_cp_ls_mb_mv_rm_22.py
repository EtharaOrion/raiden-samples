

def test_rm_recursive_with_request_payer_deletes_all_objects(cli, s3_client):
    s3_client.create_bucket(Bucket='mybucket')
    s3_client.put_object(Bucket='mybucket', Key='mykey', Body=b'hello')
    s3_client.put_object(Bucket='mybucket', Key='another/key.txt', Body=b'world')

    result = cli('s3', 'rm', 's3://mybucket/', '--recursive', '--request-payer')

    assert result.returncode == 0, result.stderr

    response = s3_client.list_objects_v2(Bucket='mybucket')
    assert response.get('KeyCount', 0) == 0
    assert 'Contents' not in response
