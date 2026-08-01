def test_create_user_pool_client_single_character_name(cli, cognito):
    import json
    import uuid

    pool_name = f"client-edge-{uuid.uuid4().hex}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        "x",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    created_client = output["UserPoolClient"]
    client_id = created_client["ClientId"]
    assert created_client["ClientName"] == "x"
    assert created_client["UserPoolId"] == pool_id
    assert client_id

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "x"
    assert described["UserPoolId"] == pool_id

    listed = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        client["ClientId"] == client_id and client["ClientName"] == "x"
        for client in listed
    )