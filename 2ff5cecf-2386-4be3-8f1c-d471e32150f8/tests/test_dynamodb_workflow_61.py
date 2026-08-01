from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_missing_table_then_list(cli, ddb_client, tmp_path):
    r1 = cli(
        "dynamodb", "get-item", "--table-name", "Wf62Ghost",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert r1.returncode != 0
    assert "ResourceNotFoundException" in r1.stderr
    r2 = cli("dynamodb", "list-tables")
    assert r2.returncode == 0
    assert "Wf62Ghost" not in ddb_client.list_tables()["TableNames"]
