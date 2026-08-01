def test_describe_user_pool_client_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-missing-pool-id"})
    pool_id = pool["UserPool"]["Id"]

    created = cognito.rpc(
        "CreateUserPoolClient",
        {"UserPoolId": pool_id, "ClientName": "existing-client"},
    )
    client_id = created["UserPoolClient"]["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--client-id",
        client_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "existing-client"
    assert described["UserPoolId"] == pool_id