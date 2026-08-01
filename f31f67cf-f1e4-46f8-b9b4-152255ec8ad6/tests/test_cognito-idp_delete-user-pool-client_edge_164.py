def test_delete_user_pool_client_removes_existing_client(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "delete-client-edge-app",
        },
    )["UserPoolClient"]
    client_id = client["ClientId"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0

    listed = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert all(
        item["ClientId"] != client_id
        for item in listed.get("UserPoolClients", [])
    )

    described_pool = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert described_pool["Id"] == pool_id
    assert described_pool["Name"] == "delete-client-edge-pool"