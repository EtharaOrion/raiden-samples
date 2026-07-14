

def test_rm_recursive_with_request_payer(cli, s3_client):
    s3_client.create_bucket(Bucket='mybucket')
    s3_client.put_object(Bucket='mybucket', Key='mykey', Body=b'hello')
    s3_client.put_object(Bucket='mybucket', Key='nested/other', Body=b'world')

    result = cli('s3', 'rm', 's3://mybucket/', '--recursive', '--request-payer')

    assert result.returncode == 0, f"stderr: {result.stderr}"

    remaining = s3_client.list_objects_v2(Bucket='mybucket')
    assert remaining.get('KeyCount', 0) == 0, f"Objects still present: {remaining.get('Contents')}"
