"""Import every module's tables so metadata is complete for migrations."""

from nsa.billing import models as billing  # noqa: F401
from nsa.contracts import models as contracts  # noqa: F401
from nsa.masterdata import models as masterdata  # noqa: F401
from nsa.platform import models as platform  # noqa: F401
from nsa.platform.workflow import models as workflow  # noqa: F401
from nsa.platform.core.db import Base
from nsa.schedule import models as schedule  # noqa: F401

metadata = Base.metadata
