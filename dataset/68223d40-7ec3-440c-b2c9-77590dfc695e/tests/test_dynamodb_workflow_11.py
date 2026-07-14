from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_fails_no_mutation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfUpdCond1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfUpdCond1", Item={"pk": {"S": "uc1"}, "n": {"N": "10"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfUpdCond1",
                 "--key", '{"pk":{"S":"uc1"}}',
                 "--update-expression", "SET n = :new",
                 "--condition-expression", "n = :exp",
                 "--expression-attribute-values", '{":new":{"N":"20"},":exp":{"N":"999"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfUpdCond1", Key={"pk": {"S": "uc1"}})
    assert from_item(resp["Item"])["n"] == 10
