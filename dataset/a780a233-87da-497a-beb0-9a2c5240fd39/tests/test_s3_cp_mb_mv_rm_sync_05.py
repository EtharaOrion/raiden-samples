

def test_cp_succeeds_when_mimetype_guess_fails(cli, s3_client, tmp_path, monkeypatch):
    s3_client.create_bucket(Bucket='bucket')
    f = tmp_path / 'foo.txt'
    f.write_text('mycontent')

    import mimetypes
    monkeypatch.setattr(mimetypes, 'guess_type', lambda x: b'\xe2'.decode('ascii'))

    result = cli('s3', 'cp', str(f), 's3://bucket/key.txt')
    assert result.returncode == 0, result.stderr

    s3_client.head_object(Bucket='bucket', Key='key.txt')
    body = s3_client.get_object(Bucket='bucket', Key='key.txt')['Body'].read()
    assert body == b'mycontent'
