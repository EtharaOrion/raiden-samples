from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_put_then_unconditional(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf74",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf74",
                 "--item", '{"pk":{"S":"k"},"v":{"S":"a"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf74", "--item", '{"pk":{"S":"k"},"v":{"S":"b"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf74", Key={"pk": {"S": "k"}})
    assert from_item(resp["Item"]) == {"pk": "k", "v": "b"}
