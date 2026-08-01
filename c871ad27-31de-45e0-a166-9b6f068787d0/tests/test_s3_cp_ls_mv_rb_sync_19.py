from _s3_http import S3HTTPError as ClientError
import pytest


def test_rb_force_removes_non_empty_bucket(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='foo', Body=b'x' * 100)

    result = cli('s3', 'rb', 's3://bucket', '--force')

    assert result.returncode == 0

    with pytest.raises(ClientError) as exc_info:
        s3_client.head_bucket(Bucket='bucket')
    assert exc_info.value.response['Error']['Code'] in ('404', 'NoSuchBucket')
