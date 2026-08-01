def test_create_user_pool_client_happy_path(cli, cognito, tmp_path):
    import json

    pool_name = f"client-pool-{tmp_path.name}"
    client_name = f"app-client-{tmp_path.name}"

    created_pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created_pool["UserPool"]["Id"]

    initial_clients = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert initial_clients.get("UserPoolClients", []) == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    client_id = output["UserPoolClient"]["ClientId"]
    assert output["UserPoolClient"]["ClientName"] == client_name
    assert output["UserPoolClient"]["UserPoolId"] == pool_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )
    persisted_client = described["UserPoolClient"]
    assert persisted_client["ClientId"] == client_id
    assert persisted_client["ClientName"] == client_name
    assert persisted_client["UserPoolId"] == pool_id

    listed = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert any(
        client["ClientId"] == client_id
        and client["ClientName"] == client_name
        for client in listed["UserPoolClients"]
    )