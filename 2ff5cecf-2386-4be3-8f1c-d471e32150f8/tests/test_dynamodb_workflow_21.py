from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_update_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf22Tbl",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf22Tbl",
        "--key", '{"pk":{"S":"a"},"sk":{"S":"b"}}',
        "--update-expression", "SET #d = :v",
        "--expression-attribute-names", '{"#d":"data"}',
        "--expression-attribute-values", '{":v":{"N":"9"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf22Tbl", Key={"pk": {"S": "a"}, "sk": {"S": "b"}})["Item"])
    assert item["data"] == 9
