def test_describe_user_pool_client_happy_path(cli, cognito, tmp_path):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"describe-client-pool-{suffix}"},
    )["UserPool"]
    client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientName": f"describe-client-{suffix}",
        },
    )["UserPoolClient"]

    result = cli(
        "cognito-idp",
        "describe-user-pool-client",
        "--user-pool-id",
        pool["Id"],
        "--client-id",
        client["ClientId"],
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["UserPoolClient"]["ClientId"] == client["ClientId"]
    assert output["UserPoolClient"]["ClientName"] == client["ClientName"]
    assert output["UserPoolClient"]["UserPoolId"] == pool["Id"]

    stored = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool["Id"],
            "ClientId": client["ClientId"],
        },
    )["UserPoolClient"]
    assert stored["ClientId"] == client["ClientId"]
    assert stored["ClientName"] == client["ClientName"]
    assert stored["UserPoolId"] == pool["Id"]