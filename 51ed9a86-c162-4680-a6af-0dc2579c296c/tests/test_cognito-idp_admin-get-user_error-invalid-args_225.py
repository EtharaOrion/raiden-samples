def test_admin_get_user_nonexistent_pool_error(cli, cognito):
    # Prerequisite: create a real pool so we know our target pool id is distinct
    pool = cognito.rpc("CreateUserPool", {"PoolName": "real-pool"})
    real_pool_id = pool["UserPool"]["Id"]

    # Use a bogus, non-existent pool id for the command under test
    bogus_pool_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    result = cli(
        "cognito-idp", "admin-get-user",
        "--user-pool-id", bogus_pool_id,
        "--username", "someuser",
    )

    # Error expected: referencing a missing pool -> ResourceNotFoundException
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "ResourceNotFoundException" in result.stderr

    # Assert the real pool has no such user (state check on the pool that does exist)
    users = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert all(u.get("Username") != "someuser" for u in users.get("Users", []))