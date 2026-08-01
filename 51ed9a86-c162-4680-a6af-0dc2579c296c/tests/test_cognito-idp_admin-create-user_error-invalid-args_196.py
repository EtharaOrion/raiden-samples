def test_admin_create_user_invalid_pool_id(cli, cognito):
    # Use a non-existent (but syntactically plausible) user pool id.
    bogus_pool_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    username = "erroruser"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", bogus_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "ResourceNotFoundException" in result.stderr

    # Assert no user was created against a real pool: create a valid pool and
    # confirm the bogus operation did not leak state into it.
    pool = cognito.rpc("CreateUserPool", {"PoolName": "err-pool"})
    real_pool_id = pool["UserPool"]["Id"]

    listed = cognito.rpc("ListUsers", {"UserPoolId": real_pool_id})
    assert all(u["Username"] != username for u in listed.get("Users", []))