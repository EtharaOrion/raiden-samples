from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_number_string_set(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf29Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf29Table",
                 "--item", '{"pk":{"S":"ss1"},"tags":{"SS":["x","y"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf29Table", Key={"pk": {"S": "ss1"}})
    assert set(from_item(resp["Item"])["tags"]) == {"x", "y"}
