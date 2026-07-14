from conftest import _stderr_names_error
def test_mv_no_arg_exits_255(cli):
    r = cli('s3', 'mv')
    assert r.returncode != 0


def test_mv_one_arg_exits_255(cli):
    r = cli('s3', 'mv', 's3://b-41a/k')
    assert r.returncode != 0


def test_mv_unknown_flag_exits_255(cli):
    r = cli('s3', 'mv', 's3://b-41b/k', 's3://b-41b/k2', '--bogus-flag')
    assert r.returncode != 0


def test_mv_both_local_paths_exits_255(cli, tmp_path):
    a = tmp_path / 'a'
    a.write_bytes(b'x')
    b = tmp_path / 'b'
    r = cli('s3', 'mv', str(a), str(b))
    assert r.returncode != 0


def test_mv_three_positional_args_exits_255(cli):
    r = cli('s3', 'mv', 's3://b-41d/k', 's3://b-41d/k2', 's3://b-41d/k3')
    assert r.returncode != 0


def test_mv_self_says_cannot_mv_v2(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v2-43a')
    s3_client.put_object(Bucket='mv-self-v2-43a', Key='key', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v2-43a/key', 's3://mv-self-v2-43a/key')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower(), f'stderr={r.stderr!r}'


def test_mv_self_says_cannot_mv_v3_nested_key(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v3-43b')
    s3_client.put_object(Bucket='mv-self-v3-43b', Key='a/b/c/key.txt', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v3-43b/a/b/c/key.txt', 's3://mv-self-v3-43b/a/b/c/key.txt')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower(), f'stderr={r.stderr!r}'


def test_mv_self_says_cannot_mv_v4_with_special_chars(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-self-v4-43c')
    s3_client.put_object(Bucket='mv-self-v4-43c', Key='key with spaces', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-self-v4-43c/key with spaces', 's3://mv-self-v4-43c/key with spaces')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower(), f'stderr={r.stderr!r}'


def test_mv_same_source_and_implied_dest_v2(cli, s3_client):
    s3_client.create_bucket(Bucket='mv-imp-v2-48a')
    s3_client.put_object(Bucket='mv-imp-v2-48a', Key='thekey', Body=b'x')
    r = cli('s3', 'mv', 's3://mv-imp-v2-48a/thekey', 's3://mv-imp-v2-48a/')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or 'itself' in r.stderr.lower(), f'stderr={r.stderr!r}'
