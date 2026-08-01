from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_map_value(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf29Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf29Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET meta = :v",
        "--expression-attribute-values", '{":v":{"M":{"k":{"S":"val"}}}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf29Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert item["meta"]["k"] == "val"
