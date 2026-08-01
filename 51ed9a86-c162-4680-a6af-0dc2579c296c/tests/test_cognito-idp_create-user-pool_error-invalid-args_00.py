def test_create_user_pool_missing_required_pool_name(cli, cognito):
    before = cognito.rpc("ListUserPools", {"MaxResults": 60})
    before_ids = {p["Id"] for p in before.get("UserPools", [])}

    result = cli("cognito-idp", "create-user-pool")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "PoolName" in result.stderr or "required" in result.stderr.lower()

    after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    after_ids = {p["Id"] for p in after.get("UserPools", [])}
    assert after_ids == before_ids