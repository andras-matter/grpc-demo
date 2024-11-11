import sqlalchemy
from dependency_injector import containers, providers

from core.dal.query import Querier
from core.env import Settings
from core.service.user_service import UserService


class Container(containers.DeclarativeContainer):
    # Settings object - created once and reused
    config = providers.Singleton(Settings)

    # Database engine - created once and reused (this is thread-safe)
    engine = providers.Singleton(
        sqlalchemy.create_engine,
        url=config.provided.db_url,
    )

    # Connection provider - creates a NEW connection each time it's requested
    # because it's a Factory. The lambda is called each time this provider is used
    connection = providers.Factory(lambda e: e.connect(), e=engine.provided)

    # Querier provider - creates a NEW querier each time with a fresh connection
    # because it's a Factory and its connection dependency is a Factory
    querier = providers.Factory(Querier, conn=connection)

    # UserService - same instance is reused (Singleton), but when it uses
    # the querier, a new querier with a fresh connection is created because
    # querier is a Factory
    user_service = providers.Singleton(UserService, querier=querier)
