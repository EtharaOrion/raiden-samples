from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_overwrite_preserves_only_new(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf69",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf69",
                 "--item", '{"pk":{"S":"o"},"old":{"S":"gone"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf69",
                 "--item", '{"pk":{"S":"o"},"fresh":{"S":"here"}}')
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf69", Key={"pk": {"S": "o"}})["Item"])
    assert "old" not in item and item["fresh"] == "here"
