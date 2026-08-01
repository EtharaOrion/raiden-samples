def test_delete_user_pool_client_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-test-pool"},
    )["UserPool"]
    user_pool_id = pool["Id"]

    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": user_pool_id,
            "ClientName": "client-to-delete",
        },
    )["UserPoolClient"]
    client_id = client["ClientId"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        user_pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0

    remaining_clients = cognito.rpc(
        "ListUserPoolClients",
        {
            "UserPoolId": user_pool_id,
            "MaxResults": 60,
        },
    )["UserPoolClients"]
    assert all(item["ClientId"] != client_id for item in remaining_clients)