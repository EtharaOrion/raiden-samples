from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_delete_then_missing(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf20Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf20Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"on"}}',
    )
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf20Tbl")
    assert result.returncode == 0
    assert "Wf20Tbl" not in ddb_client.list_tables()["TableNames"]
