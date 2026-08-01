def test_delete_user_pool_client_removes_existing_client(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-client-edge-pool"})["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "delete-client-edge-app",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode == 0

    remaining = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool["Id"], "MaxResults": 60},
    )["UserPoolClients"]
    assert all(item["ClientId"] != client["ClientId"] for item in remaining)