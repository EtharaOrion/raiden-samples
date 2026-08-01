def test_update_user_pool_client_required_ids_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "update-client-required-ids-pool"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": "update-client-required-ids-client",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["UserPoolId"] == pool["Id"]
    assert output["UserPoolClient"]["ClientId"] == client["ClientId"]

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert described["UserPoolId"] == pool["Id"]
    assert described["ClientId"] == client["ClientId"]
    assert described["ClientName"] == "update-client-required-ids-client"