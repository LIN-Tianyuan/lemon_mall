class MasterSlaveDBRouter(object):
    """Database read and write routing"""

    def db_for_read(self, model, **hints):
        """Read"""
        return "slave"

    def db_for_write(self, model, **hints):
        """Write"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Whether to run a correlation operation"""
        return True