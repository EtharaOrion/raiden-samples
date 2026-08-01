def test_describe_user_pool_empty_id_invalid(cli, cognito):
    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Invalid" in result.stderr