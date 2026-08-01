def test_describe_user_pool_client_existing_client(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-edge-pool"})["UserPool"]
    pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "describe-client-edge-app"},
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool_id
    assert output["UserPoolClient"]["ClientId"] == client_id
    assert output["UserPoolClient"]["ClientName"] == "describe-client-edge-app"

    persisted = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert persisted["UserPoolId"] == pool_id
    assert persisted["ClientId"] == client_id
    assert persisted["ClientName"] == "describe-client-edge-app"