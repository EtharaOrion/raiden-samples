from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_tables_after_create(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfList1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfList1", Item={"pk": {"S": "a"}, "v": {"S": "1"}})
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "WfList1" in ddb_client.list_tables()["TableNames"]
    upd = cli(
        "dynamodb", "update-item",
        "--table-name", "WfList1",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"2"}}',
    )
    assert upd.returncode == 0
    resp = ddb_client.get_item(TableName="WfList1", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"])["v"] == "2"
