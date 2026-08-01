from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_deep_set_multiple(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf58Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf58Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #a = :a, #b = :b, #c = :c",
        "--expression-attribute-names", '{"#a":"alpha","#b":"beta","#c":"gamma"}',
        "--expression-attribute-values", '{":a":{"N":"1"},":b":{"N":"2"},":c":{"N":"3"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf58Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["alpha"] == 1 and item["beta"] == 2 and item["gamma"] == 3
