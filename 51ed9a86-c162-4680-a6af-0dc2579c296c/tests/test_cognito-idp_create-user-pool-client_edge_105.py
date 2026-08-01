def test_create_user_pool_client_prevent_user_existence_errors_enabled(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "test-pool-puee"})
    user_pool_id = pool["UserPool"]["Id"]

    client_name = "my-app-client"
    result = cli(
        "cognito-idp", "create-user-pool-client",
        "--user-pool-id", user_pool_id,
        "--client-name", client_name,
        "--prevent-user-existence-errors", "ENABLED",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    client_id = out["UserPoolClient"]["ClientId"]
    assert out["UserPoolClient"]["ClientName"] == client_name
    assert out["UserPoolClient"]["UserPoolId"] == user_pool_id

    described = cognito.rpc("DescribeUserPoolClient", {
        "UserPoolId": user_pool_id,
        "ClientId": client_id,
    })
    assert described["UserPoolClient"]["ClientName"] == client_name
    assert described["UserPoolClient"]["ClientId"] == client_id
    assert described["UserPoolClient"]["PreventUserExistenceErrors"] == "ENABLED"