from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_fails_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf10Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf10Tbl",
                 "--item", '{"pk":{"S":"e1"},"cnt":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf10Tbl",
                 "--key", '{"pk":{"S":"e1"}}',
                 "--update-expression", "SET cnt = :new",
                 "--condition-expression", "cnt = :expected",
                 "--expression-attribute-values",
                 '{":new":{"N":"99"},":expected":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf10Tbl", Key={"pk": {"S": "e1"}})
    assert resp["Item"]["cnt"] == {"N": "1"}
