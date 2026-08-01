def test_describe_user_pool_client_rejects_empty_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-invalid-pool"})
    pool_id = pool["UserPool"]["Id"]

    created = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "describe-client-invalid-app",
        },
    )
    client_id = created["UserPoolClient"]["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        "",
        "--client-id",
        client_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )
    client = described["UserPoolClient"]
    assert client["UserPoolId"] == pool_id
    assert client["ClientId"] == client_id
    assert client["ClientName"] == "describe-client-invalid-app"