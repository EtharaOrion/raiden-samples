from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_tables_delete_one(cli, ddb_client, tmp_path):
    for t in ("Wf40a", "Wf40b"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf40a")
    assert result.returncode == 0
    names = ddb_client.list_tables()["TableNames"]
    assert "Wf40a" not in names
    assert "Wf40b" in names
