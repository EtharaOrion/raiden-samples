from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_number_gt_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf73Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf73Table",
                 "--item", '{"pk":{"S":"gf1"},"n":{"N":"3"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf73Table",
                 "--key", '{"pk":{"S":"gf1"}}',
                 "--update-expression", "SET n = :new",
                 "--condition-expression", "n > :threshold",
                 "--expression-attribute-values", '{":new":{"N":"20"},":threshold":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf73Table", Key={"pk": {"S": "gf1"}})
    assert from_item(resp["Item"])["n"] == 3
