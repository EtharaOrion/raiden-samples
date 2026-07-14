from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_delete_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf_Ephemeral",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf_Ephemeral" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", "Wf_Ephemeral")
    assert result.returncode == 0
    assert "Wf_Ephemeral" not in ddb_client.list_tables()["TableNames"]
