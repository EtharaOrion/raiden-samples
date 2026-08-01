from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_three_tables_partial_delete(cli, ddb_client, tmp_path):
    for t in ("Wf76a", "Wf76b", "Wf76c"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf76b")
    assert result.returncode == 0
    names = ddb_client.list_tables()["TableNames"]
    assert "Wf76a" in names and "Wf76c" in names and "Wf76b" not in names
