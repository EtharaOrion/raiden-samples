from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_string_set(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfSS1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfSS1",
                 "--item", '{"pk":{"S":"ss"},"tags":{"SS":["x","y","z"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfSS1", Key={"pk": {"S": "ss"}})
    got = from_item(resp["Item"])
    assert set(got["tags"]) == {"x", "y", "z"}
