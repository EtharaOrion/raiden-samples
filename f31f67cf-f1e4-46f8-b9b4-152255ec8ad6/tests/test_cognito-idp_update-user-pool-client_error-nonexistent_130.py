def test_update_user_pool_client_nonexistent_client(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-nonexistent-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    existing_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        "nonexistentclient123456",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    preserved = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientId": existing_client["ClientId"],
        },
    )["UserPoolClient"]
    assert preserved["ClientId"] == existing_client["ClientId"]
    assert preserved["ClientName"] == "existing-client"
    assert preserved["UserPoolId"] == pool_id