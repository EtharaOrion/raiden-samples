def test_create_user_pool_client_happy_path(cli, cognito):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    pool_name = f"pool-{suffix}"
    client_name = f"client-{suffix}"

    created_pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    user_pool_id = created_pool["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        user_pool_id,
        "--client-name",
        client_name,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    created_client = output["UserPoolClient"]
    client_id = created_client["ClientId"]
    assert created_client["ClientName"] == client_name
    assert created_client["UserPoolId"] == user_pool_id
    assert client_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": user_pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == client_name
    assert described["UserPoolId"] == user_pool_id