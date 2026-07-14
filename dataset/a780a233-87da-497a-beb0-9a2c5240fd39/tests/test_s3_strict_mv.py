from conftest import _stderr_names_error
def test_mv_self_v2(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v2-43a')
    s3_client.put_object(Bucket='mv-self-v2-43a', Key='key', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v2-43a/key', 's3://mv-self-v2-43a/key')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower()


def test_mv_self_v3_nested(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v3-43b')
    s3_client.put_object(Bucket='mv-self-v3-43b', Key='a/b/c.txt', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v3-43b/a/b/c.txt', 's3://mv-self-v3-43b/a/b/c.txt')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower()


def test_mv_self_v4_spaces(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v4-43c')
    s3_client.put_object(Bucket='mv-self-v4-43c', Key='key with spaces', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v4-43c/key with spaces', 's3://mv-self-v4-43c/key with spaces')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower()


def test_mv_same_src_implied_dest_v2(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-imp-v2-48a')
    s3_client.put_object(Bucket='mv-imp-v2-48a', Key='thekey', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-imp-v2-48a/thekey', 's3://mv-imp-v2-48a/')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower()
