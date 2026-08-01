from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_listtables_membership(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf2Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf2Tbl" in ddb_client.list_tables()["TableNames"]
