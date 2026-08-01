from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_creates_then_verify_pk(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf66Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf66Table",
                 "--key", '{"pk":{"S":"cp1"}}',
                 "--update-expression", "SET made = :m",
                 "--expression-attribute-values", '{":m":{"BOOL":true}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf66Table", Key={"pk": {"S": "cp1"}})
    item = from_item(resp["Item"])
    assert item["pk"] == "cp1" and item["made"] is True
