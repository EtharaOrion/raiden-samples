def test_mb_no_arg_exits_255(cli):
    r = cli('s3', 'mb')
    assert r.returncode != 0, f'expected non-zero, got {r.returncode}; stderr={r.stderr!r}'


def test_mb_bare_no_scheme_v2_exits_255(cli):
    r = cli('s3', 'mb', 'no-scheme-here-v2-40a')
    assert r.returncode != 0


def test_mb_too_short_exits_255(cli):
    r = cli('s3', 'mb', 's3://ab')
    assert r.returncode != 0


def test_mb_too_long_exits_255(cli):
    long_name = 'a' + 'b' * 63 + 'c'
    r = cli('s3', 'mb', f's3://{long_name}')
    assert r.returncode != 0
