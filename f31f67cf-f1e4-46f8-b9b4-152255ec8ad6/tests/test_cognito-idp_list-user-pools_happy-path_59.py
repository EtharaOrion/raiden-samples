def test_list_user_pools_happy_path(cli, cognito, tmp_path):
    import json
    import uuid

    pool_name = f"list-happy-{uuid.uuid4().hex}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    try:
        result = cli(
            "cognito-idp",
            "list-user-pools",
            "--max-results",
            "60",
        )

        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        listed_pools = output["UserPools"]
        assert any(
            pool["Id"] == pool_id and pool["Name"] == pool_name
            for pool in listed_pools
        )

        described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
        assert described["UserPool"]["Id"] == pool_id
        assert described["UserPool"]["Name"] == pool_name
    finally:
        cognito.rpc("DeleteUserPool", {"UserPoolId": pool_id})