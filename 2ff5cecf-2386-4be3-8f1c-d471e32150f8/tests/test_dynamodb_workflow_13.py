from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_multiple_attrs_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf14Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf14Tbl", Item={"pk": {"S": "a"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf14Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :s, #c = :c",
        "--expression-attribute-names", '{"#s":"status","#c":"count"}',
        "--expression-attribute-values", '{":s":{"S":"ok"},":c":{"N":"3"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf14Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["status"] == "ok"
    assert item["count"] == 3
