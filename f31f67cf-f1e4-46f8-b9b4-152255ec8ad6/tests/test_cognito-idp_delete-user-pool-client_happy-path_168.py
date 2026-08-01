def test_delete_user_pool_client_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "client-to-delete",
        },
    )["UserPoolClient"]
    client_id = client["ClientId"]

    existing = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientId": client_id,
        },
    )["UserPoolClient"]
    assert existing["ClientId"] == client_id
    assert existing["ClientName"] == "client-to-delete"
    assert existing["UserPoolId"] == pool_id

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0

    remaining_clients = cognito.rpc(
        "ListUserPoolClients",
        {
            "UserPoolId": pool_id,
            "MaxResults": 60,
        },
    )["UserPoolClients"]
    assert all(item["ClientId"] != client_id for item in remaining_clients)