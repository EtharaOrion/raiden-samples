def test_list_queue_tags_missing_required_queue_url(cli, sqs):
    result = cli("sqs", "list-queue-tags")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-url" in result.stderr.lower()