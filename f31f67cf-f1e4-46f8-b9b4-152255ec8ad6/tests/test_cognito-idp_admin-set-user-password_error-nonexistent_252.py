def test_admin_set_user_password_nonexistent_pool(cli, cognito):
    pool_name = "admin-set-password-error-pool"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    existing_pool_id = created["UserPool"]["Id"]
    nonexistent_pool_id = existing_pool_id + "x"

    result = cli(
        "cognito-idp",
        "admin-set-user-password",
        "--user-pool-id",
        nonexistent_pool_id,
        "--username",
        "missing-user",
        "--password",
        "ValidPassword123!",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": existing_pool_id},
    )
    assert described["UserPool"]["Id"] == existing_pool_id
    assert described["UserPool"]["Name"] == pool_name