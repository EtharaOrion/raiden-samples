from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_fails_no_mutation(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_UpdCond",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf_UpdCond",
                 "--item", '{"pk":{"S":"uc1"},"cnt":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf_UpdCond",
                 "--key", '{"pk":{"S":"uc1"}}',
                 "--update-expression", "SET cnt = :v",
                 "--expression-attribute-values", '{":v":{"N":"99"},":old":{"N":"5"}}',
                 "--condition-expression", "cnt = :old")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf_UpdCond", Key={"pk": {"S": "uc1"}})
    assert from_item(resp["Item"])["cnt"] == 1
