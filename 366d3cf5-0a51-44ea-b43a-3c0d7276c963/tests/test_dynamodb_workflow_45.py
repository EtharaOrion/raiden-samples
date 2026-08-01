from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddb_create_cli_deletetable(cli, ddb_client, tmp_path):
    ddb_client.create_table(TableName="Wf46",
                            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                            BillingMode="PAY_PER_REQUEST")
    assert "Wf46" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "Wf46")
    assert result.returncode == 0
    assert "Wf46" not in ddb_client.list_tables()["TableNames"]
