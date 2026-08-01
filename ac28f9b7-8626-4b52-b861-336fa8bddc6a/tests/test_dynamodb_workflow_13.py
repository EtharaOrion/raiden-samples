from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_number_increment(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf14Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf14Table",
                 "--item", '{"pk":{"S":"i1"},"count":{"N":"10"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf14Table",
                 "--key", '{"pk":{"S":"i1"}}',
                 "--update-expression", "SET #c = #c + :inc",
                 "--expression-attribute-names", '{"#c":"count"}',
                 "--expression-attribute-values", '{":inc":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf14Table", Key={"pk": {"S": "i1"}})
    assert from_item(resp["Item"])["count"] == 15
