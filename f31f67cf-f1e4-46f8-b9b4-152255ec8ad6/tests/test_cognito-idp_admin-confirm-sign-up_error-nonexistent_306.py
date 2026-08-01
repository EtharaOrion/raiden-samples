def test_admin_confirm_sign_up_nonexistent_user_pool(cli, cognito, tmp_path):
    control_name = f"confirm-control-{tmp_path.name}"
    target_name = f"confirm-deleted-{tmp_path.name}"

    control_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": control_name},
    )["UserPool"]
    target_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": target_name},
    )["UserPool"]

    target_pool_id = target_pool["Id"]
    cognito.rpc("DeleteUserPool", {"UserPoolId": target_pool_id})

    result = cli(
        "cognito-idp",
        "admin-confirm-sign-up",
        "--user-pool-id",
        target_pool_id,
        "--username",
        "nonexistent-user",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    remaining_control = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": control_pool["Id"]},
    )["UserPool"]
    assert remaining_control["Id"] == control_pool["Id"]
    assert remaining_control["Name"] == control_name