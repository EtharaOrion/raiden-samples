from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_reflects_multiple_creates(cli, ddb_client, tmp_path):
    names = ["Wf20A", "Wf20B", "Wf20C"]
    for name in names:
        result = cli("dynamodb", "create-table", "--table-name", name,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    existing = set(ddb_client.list_tables()["TableNames"])
    assert set(names).issubset(existing)
