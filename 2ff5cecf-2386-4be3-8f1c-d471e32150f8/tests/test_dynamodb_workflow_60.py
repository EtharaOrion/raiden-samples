from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_bool_toggle(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf61Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf61Tbl", Item={"pk": {"S": "a"}, "active": {"BOOL": True}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf61Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET active = :v",
        "--expression-attribute-values", '{":v":{"BOOL":false}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf61Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["active"] is False
