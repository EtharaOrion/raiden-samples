from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_list_present(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf26Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf26Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET x = :v",
        "--expression-attribute-values", '{":v":{"N":"1"}}',
    )
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf26Tbl" in ddb_client.list_tables()["TableNames"]
