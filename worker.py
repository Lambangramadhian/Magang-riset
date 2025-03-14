import redis
from rq import Queue
from rq.worker import SimpleWorker
from rq.timeouts import BaseDeathPenalty
from app_factory import create_app

# Koneksi Redis
redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)

# DummyDeathPenalty untuk menghindari masalah penanganan sinyal (terutama untuk Windows)
class DummyDeathPenalty(BaseDeathPenalty):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class WorkerWithoutSignals(SimpleWorker):
    """Worker kustom yang tidak memasang signal handler (untuk thread latar belakang)."""
    def _install_signal_handlers(self):
        pass

def start_worker():
    """Mulai worker dengan konteks aplikasi Flask."""
    app, _ = create_app()

    with app.app_context():
        queue = Queue('default', connection=redis_connection)
        worker = WorkerWithoutSignals([queue], connection=redis_connection)
        worker.death_penalty_class = DummyDeathPenalty
        worker.work(with_scheduler=False)