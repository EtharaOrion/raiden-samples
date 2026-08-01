def test_update_user_pool_client_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-happy-path-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode == 0

    updated = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert updated["UserPoolId"] == pool["Id"]
    assert updated["ClientId"] == client["ClientId"]
    assert updated["ClientName"] == "existing-client"