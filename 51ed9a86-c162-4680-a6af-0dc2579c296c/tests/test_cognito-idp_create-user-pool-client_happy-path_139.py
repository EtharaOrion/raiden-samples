def test_create_user_pool_client_happy_path(cli, cognito, tmp_path):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-cupc"})
    pool_id = pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", pool_id,
        "--client-name", "my-app-client",
        "--explicit-auth-flows", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH",
        "--refresh-token-validity", "30",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    client = out["UserPoolClient"]
    client_id = client["ClientId"]
    assert client["ClientName"] == "my-app-client"
    assert client["UserPoolId"] == pool_id

    described = cognito.rpc("DescribeUserPoolClient", {
        "UserPoolId": pool_id,
        "ClientId": client_id,
    })
    dc = described["UserPoolClient"]
    assert dc["ClientId"] == client_id
    assert dc["ClientName"] == "my-app-client"
    assert dc["UserPoolId"] == pool_id