from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_exists_update(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfCe1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfCe1",
                 "--item", '{"pk":{"S":"e"},"v":{"S":"one"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfCe1",
                 "--item", '{"pk":{"S":"e"},"v":{"S":"two"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfCe1", Key={"pk": {"S": "e"}})
    assert from_item(resp["Item"]) == {"pk": "e", "v": "two"}
