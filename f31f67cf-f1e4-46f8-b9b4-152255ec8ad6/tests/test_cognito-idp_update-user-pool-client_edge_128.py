def test_update_user_pool_client_sets_legacy_user_existence_errors(cli, cognito, tmp_path):
    pool_name = f"update-client-{tmp_path.name}"
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    created_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "edge-client",
            "PreventUserExistenceErrors": "ENABLED",
        },
    )["UserPoolClient"]
    client_id = created_client["ClientId"]

    before = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert before["PreventUserExistenceErrors"] == "ENABLED"

    result = cli(
        "cognito-idp",
        "update-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        client_id,
        "--prevent-user-existence-errors",
        "LEGACY",
    )
    assert result.returncode == 0

    updated = cognito.rpc(
        "DescribeUserPoolClient",
        {"UserPoolId": pool_id, "ClientId": client_id},
    )["UserPoolClient"]
    assert updated["UserPoolId"] == pool_id
    assert updated["ClientId"] == client_id
    assert updated["PreventUserExistenceErrors"] == "LEGACY"