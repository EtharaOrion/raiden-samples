def test_create_user_pool_client_with_legacy_user_existence_errors(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "create-client-legacy-test-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    before = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )
    assert before["UserPoolClients"] == []

    result = cli(
        "cognito-idp",
        "create-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-name",
        "legacy-existence-errors-client",
        "--prevent-user-existence-errors",
        "LEGACY",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    created = output["UserPoolClient"]
    client_id = created["ClientId"]
    assert created["ClientName"] == "legacy-existence-errors-client"
    assert created["UserPoolId"] == pool_id
    assert created["PreventUserExistenceErrors"] == "LEGACY"

    described = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert described["ClientId"] == client_id
    assert described["ClientName"] == "legacy-existence-errors-client"
    assert described["UserPoolId"] == pool_id
    assert described["PreventUserExistenceErrors"] == "LEGACY"

    listed = cognito.rpc(
        "ListUserPoolClients",
        {"UserPoolId": pool_id, "MaxResults": 60},
    )["UserPoolClients"]
    assert any(
        client["ClientId"] == client_id
        and client["ClientName"] == "legacy-existence-errors-client"
        for client in listed
    )