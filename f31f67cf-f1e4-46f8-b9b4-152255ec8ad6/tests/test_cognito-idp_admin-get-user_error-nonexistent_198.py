def test_admin_get_user_nonexistent_pool(cli, cognito):
    created = cognito.rpc("CreateUserPool", {"PoolName": "admin-get-user-error-pool"})
    pool_id = created["UserPool"]["Id"]
    missing_pool_id = f"{pool_id}missing"

    result = cli(
        "cognito-idp",
        "admin-get-user",
        "--user-pool-id",
        missing_pool_id,
        "--username",
        "nonexistent-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == "admin-get-user-error-pool"