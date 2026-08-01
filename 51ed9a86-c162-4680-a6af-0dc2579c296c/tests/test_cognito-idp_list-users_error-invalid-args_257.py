def test_list_users_invalid_pool_id(cli, cognito):
    bad_pool_id = "x" * 54
    result = cli("cognito-idp", "list-users", "--user-pool-id", bad_pool_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "InvalidParameterException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )

    # Assert no such pool exists / cannot be described in real state
    try:
        cognito.rpc("DescribeUserPool", {"UserPoolId": bad_pool_id})
        described = True
    except Exception:
        described = False
    assert not described