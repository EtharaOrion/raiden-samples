from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_names_success(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf61",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf61",
                 "--item", '{"pk":{"S":"n"},"v":{"S":"first"}}',
                 "--condition-expression", "attribute_not_exists(#p)",
                 "--expression-attribute-names", '{"#p":"pk"}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf61", Key={"pk": {"S": "n"}})
    assert from_item(resp["Item"]) == {"pk": "n", "v": "first"}
