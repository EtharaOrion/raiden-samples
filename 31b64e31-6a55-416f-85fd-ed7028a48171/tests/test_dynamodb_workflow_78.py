from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_names_values_notexists(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf79Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf79Tbl",
                 "--item", '{"pk":{"S":"c"},"status":{"S":"active"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf79Tbl",
                 "--item", '{"pk":{"S":"c"},"status":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(#s)",
                 "--expression-attribute-names", '{"#s":"pk"}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf79Tbl", Key={"pk": {"S": "c"}})
    assert resp["Item"]["status"]["S"] == "active"
