import os
import sys

__abs_file__ = os.path.abspath(__file__)
lib_dir = os.path.dirname(__abs_file__)
sys.path.append(lib_dir)
code_dir = os.path.dirname(lib_dir)
sys.path.append(code_dir)

from conf import db as _db_conf

if _db_conf.DB_TYPE == "sqlite":
    from lib import yom_sqlite as orm
    from lib.yom_sqlite import (
        Model,
        IntField,
        CharField,
        DoubleField,
        TimeStampField,
        StringField,
    )
else:
    from lib import yom as orm
    from lib.yom import (
        Model,
        IntField,
        CharField,
        DoubleField,
        TimeStampField,
        StringField,
    )
