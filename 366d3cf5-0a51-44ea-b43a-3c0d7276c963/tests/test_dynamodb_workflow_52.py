from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_all_tables_empty_list(cli, ddb_client, tmp_path):
    for t in ("Wf53a", "Wf53b"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf53a")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf53b")
    assert result.returncode == 0
    names = ddb_client.list_tables()["TableNames"]
    assert "Wf53a" not in names and "Wf53b" not in names
