from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_creates_item_then_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf4Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf4Tbl",
        "--key", '{"pk":{"S":"new"}}',
        "--update-expression", "SET #n = :v",
        "--expression-attribute-names", '{"#n":"count"}',
        "--expression-attribute-values", '{":v":{"N":"7"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf4Tbl", Key={"pk": {"S": "new"}})
    assert from_item(resp["Item"])["count"] == 7
