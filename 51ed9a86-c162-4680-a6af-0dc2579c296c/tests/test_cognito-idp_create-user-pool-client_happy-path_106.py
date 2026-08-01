def test_create_user_pool_client_happy_path(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-cupc"})
    pool_id = pool["UserPool"]["Id"]

    client_name = "my-app-client"
    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-name", client_name,
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    created = out["UserPoolClient"]
    client_id = created["ClientId"]
    assert created["ClientName"] == client_name
    assert created["UserPoolId"] == pool_id

    described = cognito.rpc("DescribeUserPoolClient", {
        "UserPoolId": pool_id,
        "ClientId": client_id,
    })
    assert described["UserPoolClient"]["ClientId"] == client_id
    assert described["UserPoolClient"]["ClientName"] == client_name
    assert described["UserPoolClient"]["UserPoolId"] == pool_id