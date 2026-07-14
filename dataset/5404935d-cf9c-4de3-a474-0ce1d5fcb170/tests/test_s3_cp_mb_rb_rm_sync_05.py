

def test_cp_succeeds_when_mimetype_guess_fails(cli, s3_client, tmp_path):
    s3_client.create_bucket(Bucket='bucket')
    src = tmp_path / 'foo.txt'
    src.write_text('mycontent')

    result = cli('s3', 'cp', str(src), 's3://bucket/key.txt')

    assert result.returncode == 0, result.stderr

    head = s3_client.head_object(Bucket='bucket', Key='key.txt')
    assert head['ContentLength'] == len('mycontent')

    body = s3_client.get_object(Bucket='bucket', Key='key.txt')['Body'].read()
    assert body == b'mycontent'
