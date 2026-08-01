from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_updates_attribute_via_overwrite(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl24",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl24",
                 "--item", '{"pk":{"S":"u1"},"status":{"S":"pending"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl24",
                 "--item", '{"pk":{"S":"u1"},"status":{"S":"done"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl24", Key={"pk": {"S": "u1"}})
    assert resp["Item"]["status"]["S"] == "done"
