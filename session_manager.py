class SessionManager:
    def __init__(
            self,
            user_id: int,
            cloud_sync: CloudSyncManager,
            db_manager: DbManager 
            ):
        self._current_user = current_user
        self._cloud_sync = cloud_sync
        self._db_manager = db_manager