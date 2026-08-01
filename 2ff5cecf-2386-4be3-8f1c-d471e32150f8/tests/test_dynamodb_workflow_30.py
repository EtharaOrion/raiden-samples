from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_empty_list_tables_ok(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert isinstance(ddb_client.list_tables()["TableNames"], list)
