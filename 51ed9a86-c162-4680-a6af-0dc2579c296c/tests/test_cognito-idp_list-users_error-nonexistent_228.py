def test_list_users_error_nonexistent(cli, cognito):
    # Use a well-formed but nonexistent user pool ID
    missing_pool_id = "local_nonexistentpool"

    # Confirm the pool truly does not exist via a direct RPC
    try:
        cognito.rpc("DescribeUserPool", {"UserPoolId": missing_pool_id})
        pool_exists = True
    except Exception:
        pool_exists = False
    assert not pool_exists

    # Run the command under test against the nonexistent pool
    result = cli("cognito-idp", "list-users", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr