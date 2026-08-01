from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_conditional_put_succeeds_new(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl17",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl17",
                 "--item", '{"pk":{"S":"cn1"},"v":{"S":"created"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl17", Key={"pk": {"S": "cn1"}})
    assert resp["Item"]["v"]["S"] == "created"
