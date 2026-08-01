def test_create_user_pool_client_minimum_length_name(cli, cognito):
    import json
    import uuid

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"client-edge-{uuid.uuid4().hex}"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert before.get("UserPoolClients", []) == []

    client_name = "x"
    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        client_name,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created = output["UserPoolClient"]
    client_id = created["ClientId"]
    assert created["ClientName"] == client_name
    assert created["UserPoolId"] == pool_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == client_name
    assert described["UserPoolId"] == pool_id