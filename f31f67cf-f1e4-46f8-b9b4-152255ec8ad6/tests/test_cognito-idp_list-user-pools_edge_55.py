def test_list_user_pools_with_next_token_succeeds(cli, cognito, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    pool_name = f"edge-pool-{suffix}"
    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "list-user-pools",
        "--max-results",
        "60",
        "--next-token",
        "x",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output["UserPools"], list)
    assert any(
        pool["Id"] == pool_id and pool["Name"] == pool_name
        for pool in output["UserPools"]
    )

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Id"] == pool_id
    assert described["UserPool"]["Name"] == pool_name