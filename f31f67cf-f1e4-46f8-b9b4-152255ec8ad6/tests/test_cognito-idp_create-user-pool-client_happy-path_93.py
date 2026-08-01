def test_create_user_pool_client_happy_path(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "client-test-pool"})["UserPool"]
    pool_id = pool["Id"]
    client_name = "client-test-app"

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created_client = output["UserPoolClient"]
    client_id = created_client["ClientId"]
    assert created_client["ClientName"] == client_name
    assert created_client["UserPoolId"] == pool_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == client_name
    assert described["UserPoolId"] == pool_id