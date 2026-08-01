def test_update_user_pool_client_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-invalid-args-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "unchanged-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    persisted = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert persisted["UserPoolId"] == pool["Id"]
    assert persisted["ClientId"] == client["ClientId"]
    assert persisted["ClientName"] == "unchanged-client"