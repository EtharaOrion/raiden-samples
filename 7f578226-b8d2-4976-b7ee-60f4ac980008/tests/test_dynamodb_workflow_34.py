from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_helper_marshal_roundtrip(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl32",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl32",
                 "--item", '{"pk":{"S":"h1"},"score":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl32", Key={"pk": {"S": "h1"}})
    native = from_item(resp["Item"])
    assert native["pk"] == "h1"
    assert str(native["score"]) == "42"
