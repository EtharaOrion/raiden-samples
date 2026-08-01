def test_delete_user_pool_client_rejects_empty_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-client-invalid-pool"})["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "delete-client-invalid-app",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        "",
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    remaining = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert remaining["UserPoolId"] == pool["Id"]
    assert remaining["ClientId"] == client["ClientId"]
    assert remaining["ClientName"] == "delete-client-invalid-app"