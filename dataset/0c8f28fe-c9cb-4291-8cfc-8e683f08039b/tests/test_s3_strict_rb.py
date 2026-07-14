from conftest import _stderr_names_error
def test_rb_no_arg_exits_255(cli):
    r = cli('s3', 'rb')
    assert r.returncode != 0


def test_rb_unknown_flag_exits_255(cli):
    r = cli('s3', 'rb', 's3://b-42a', '--bogus-flag')
    assert r.returncode != 0


def test_rb_no_scheme_exits_255(cli):
    r = cli('s3', 'rb', 'no-scheme-42b')
    assert r.returncode != 0


def test_rb_nonexistent_says_failed_v2(cli):
    r = cli('s3', 'rb', 's3://nonexistent-v2-44a-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr), f'stderr={r.stderr!r}'


def test_rb_nonexistent_says_failed_v3_unicode(cli):
    r = cli('s3', 'rb', 's3://nonexistent-44b-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr), f'stderr={r.stderr!r}'


def test_rb_nonexistent_says_failed_v4(cli):
    r = cli('s3', 'rb', 's3://nonexistent-44c-stump')
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr), f'stderr={r.stderr!r}'


def test_rb_force_nonexistent_v2_exits_255(cli):
    r = cli('s3', 'rb', 's3://nonexistent-force-v2-46a', '--force')
    assert r.returncode != 0


def test_rb_force_nonexistent_v3_exits_255(cli):
    r = cli('s3', 'rb', 's3://nonexistent-force-46b', '--force')
    assert r.returncode != 0
