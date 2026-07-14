from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_new_attribute_getitem(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfUpd2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfUpd2", Item={"pk": {"S": "u2"}})
    result = cli("dynamodb", "update-item", "--table-name", "WfUpd2",
                 "--key", '{"pk":{"S":"u2"}}',
                 "--update-expression", "SET score = :v",
                 "--expression-attribute-values", '{":v":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfUpd2", Key={"pk": {"S": "u2"}})
    assert from_item(resp["Item"]) == {"pk": "u2", "score": 42}
