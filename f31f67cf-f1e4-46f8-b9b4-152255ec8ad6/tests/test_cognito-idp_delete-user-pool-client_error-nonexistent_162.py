def test_delete_user_pool_client_nonexistent(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "delete-nonexistent-client-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    existing_client = cognito.rpc(
        "CreateUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientName": "existing-client",
        },
    )["UserPoolClient"]
    existing_client_id = existing_client["ClientId"]

    nonexistent_client_id = "0" * 26
    if nonexistent_client_id == existing_client_id:
        nonexistent_client_id = "1" * 26

    result = cli(
        "cognito-idp",
        "delete-user-pool-client",
        "--user-pool-id",
        pool_id,
        "--client-id",
        nonexistent_client_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    remaining_client = cognito.rpc(
        "DescribeUserPoolClient",
        {
            "UserPoolId": pool_id,
            "ClientId": existing_client_id,
        },
    )["UserPoolClient"]
    assert remaining_client["ClientId"] == existing_client_id
    assert remaining_client["ClientName"] == "existing-client"
    assert remaining_client["UserPoolId"] == pool_id