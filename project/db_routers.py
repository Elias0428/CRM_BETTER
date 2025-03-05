class ExternalDatabaseRouter:
    def db_for_read(self, model, **hints):
        """
        Reenvía las consultas de lectura a la base de datos externa.
        """
        if model._meta.app_label == 'app':
            return 'external_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Evita que se escriba en la base de datos externa.
        """
        if model._meta.app_label == 'app':
            return 'external_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        No permitas migraciones en la base de datos externa.
        """
        if db == 'external_db':
            return False
        return None
