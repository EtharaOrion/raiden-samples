from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_two_delete_first_put_second(cli, ddb_client, tmp_path):
    for t in ("Wf72a", "Wf72b"):
        result = cli("dynamodb", "create-table", "--table-name", t,
                     "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                     "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                     "--billing-mode", "PAY_PER_REQUEST")
        assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf72a")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf72b", "--item", '{"pk":{"S":"ok"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf72b", Key={"pk": {"S": "ok"}})
    result = cli("dynamodb", "put-item", "--table-name", "Wf72a", "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
