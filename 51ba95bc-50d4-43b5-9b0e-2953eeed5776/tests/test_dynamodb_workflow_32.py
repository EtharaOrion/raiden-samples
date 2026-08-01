from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_nested_structure_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_nest1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_nest1",
                 "--item",
                 '{"pk":{"S":"ne1"},"doc":{"M":{"items":{"L":[{"N":"1"},{"N":"2"}]},"name":{"S":"box"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_nest1", Key={"pk": {"S": "ne1"}})
    assert from_item(resp["Item"]) == {"pk": "ne1", "doc": {"items": [1, 2], "name": "box"}}
