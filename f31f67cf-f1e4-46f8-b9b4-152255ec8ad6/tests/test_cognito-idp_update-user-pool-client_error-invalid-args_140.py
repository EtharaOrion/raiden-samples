def test_update_user_pool_client_rejects_invalid_attribute_definitions(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-invalid-args-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "update-client-invalid-args-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    unchanged = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert unchanged["UserPoolId"] == pool["Id"]
    assert unchanged["ClientId"] == client["ClientId"]
    assert unchanged["ClientName"] == "update-client-invalid-args-client"