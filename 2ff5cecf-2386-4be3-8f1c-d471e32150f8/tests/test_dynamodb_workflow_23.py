from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_attribute_not_exists_success(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf24Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf24Tbl", Item={"pk": {"S": "a"}})
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf24Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET fresh = :v",
        "--condition-expression", "attribute_not_exists(fresh)",
        "--expression-attribute-values", '{":v":{"S":"yes"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf24Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["fresh"] == "yes"
