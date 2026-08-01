from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_negative_number(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf36Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf36Table",
                 "--item", '{"pk":{"S":"neg1"},"bal":{"N":"0"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf36Table",
                 "--key", '{"pk":{"S":"neg1"}}',
                 "--update-expression", "SET bal = :b",
                 "--expression-attribute-values", '{":b":{"N":"-25"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf36Table", Key={"pk": {"S": "neg1"}})
    assert from_item(resp["Item"])["bal"] == -25
