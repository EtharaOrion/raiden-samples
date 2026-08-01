def test_describe_user_pool_client_missing_required_client_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "describe-client-invalid-args"})
    pool_id = pool["UserPool"]["Id"]

    created = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "existing-client",
        },
    )
    client_id = created["UserPoolClient"]["ClientId"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--client-id" in result.stderr

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientId": client_id,
        },
    )
    client = described["UserPoolClient"]
    assert client["ClientId"] == client_id
    assert client["ClientName"] == "existing-client"
    assert client["UserPoolId"] == pool_id