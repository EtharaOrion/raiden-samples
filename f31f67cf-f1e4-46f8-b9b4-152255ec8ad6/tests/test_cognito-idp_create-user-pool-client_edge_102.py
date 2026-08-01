def test_create_user_pool_client_with_generated_pool_id(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-client-edge-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        "edge-client",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    created_client = output["UserPoolClient"]
    client_id = created_client["ClientId"]
    assert created_client["ClientName"] == "edge-client"
    assert created_client["UserPoolId"] == pool_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "edge-client"
    assert described["UserPoolId"] == pool_id