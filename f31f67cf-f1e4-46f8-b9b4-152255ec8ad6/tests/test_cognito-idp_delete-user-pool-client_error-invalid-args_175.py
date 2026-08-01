def test_delete_user_pool_client_rejects_unknown_attribute_definitions(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-client-invalid-args-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "delete-client-invalid-args-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
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

    remaining = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert remaining["ClientId"] == client["ClientId"]
    assert remaining["ClientName"] == "delete-client-invalid-args-client"
    assert remaining["UserPoolId"] == pool["Id"]