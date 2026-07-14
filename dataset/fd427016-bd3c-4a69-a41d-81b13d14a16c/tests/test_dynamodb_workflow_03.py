from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "get-item", "--table-name", "NoSuchTblGet",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTblGet" not in ddb_client.list_tables()["TableNames"]
