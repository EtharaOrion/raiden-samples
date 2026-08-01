from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_replace_map(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf52Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf52Tbl", Item={"pk": {"S": "a"}, "m": {"M": {"k": {"S": "old"}}}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf52Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET m = :v",
        "--expression-attribute-values", '{":v":{"M":{"k":{"S":"new"}}}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf52Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["m"]["k"] == "new"
