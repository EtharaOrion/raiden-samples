from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_with_underscore_attr(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_uattr1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_uattr1",
                 "--item", '{"pk":{"S":"ua1"},"created_at":{"N":"1609459200"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_uattr1", Key={"pk": {"S": "ua1"}})
    assert from_item(resp["Item"]) == {"pk": "ua1", "created_at": 1609459200}
