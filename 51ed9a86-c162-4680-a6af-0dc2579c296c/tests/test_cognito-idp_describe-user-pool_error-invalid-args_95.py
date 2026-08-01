def test_describe_user_pool_nonexistent_id_error(cli, cognito):
    missing_pool_id = "local_nonexistentpool123"

    result = cli("cognito-idp", "describe-user-pool", "--user-pool-id", missing_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    pools = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids = [p["Id"] for p in pools.get("UserPools", [])]
    assert missing_pool_id not in ids