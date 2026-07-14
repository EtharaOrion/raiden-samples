

def test_s3_ls_recursive_lists_all_objects(cli, s3_client):
    s3_client.create_bucket(Bucket='bucket')
    s3_client.put_object(Bucket='bucket', Key='foo/bar.txt', Body=b'a' * 100)
    s3_client.put_object(Bucket='bucket', Key='foo/baz/qux.txt', Body=b'b' * 50)
    s3_client.put_object(Bucket='bucket', Key='top.txt', Body=b'c' * 10)

    result = cli('s3', 'ls', 's3://bucket/', '--recursive')

    assert result.returncode == 0, result.stderr
    assert 'foo/bar.txt' in result.stdout
    assert 'foo/baz/qux.txt' in result.stdout
    assert 'top.txt' in result.stdout
    assert '100' in result.stdout
    assert '50' in result.stdout
    assert '10' in result.stdout
