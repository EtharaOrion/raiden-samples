from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_string_set(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf33Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf33Tbl",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET tags = :v",
        "--expression-attribute-values", '{":v":{"SS":["x","y","z"]}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf33Tbl", Key={"pk": {"S": "a"}})["Item"])
    assert set(item["tags"]) == {"x", "y", "z"}
