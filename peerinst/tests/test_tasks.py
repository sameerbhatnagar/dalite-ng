from peerinst.tasks import compute_gradebook_async


def test_compute_gradebook_async(celery_worker):
    task_id = compute_gradebook_async(None, None).id

    assert isinstance(task_id, basestring)
