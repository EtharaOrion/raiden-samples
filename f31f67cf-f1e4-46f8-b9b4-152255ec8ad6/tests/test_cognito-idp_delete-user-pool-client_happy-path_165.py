def test_delete_user_pool_client_happy_path(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-happy-path"},
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

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0

    remaining = cognito.rpc(
        "ListUserPoolClients",
        {
            "UserPoolId": pool_id,
            "MaxResults": 60,
        },
    )["UserPoolClients"]
    assert all(item["ClientId"] != client_id for item in remaining)

    described_pool = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": pool_id},
    )["UserPool"]
    assert described_pool["Id"] == pool_id