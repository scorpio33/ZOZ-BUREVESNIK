from dependency_injector import containers, providers
from core.task_management_service import TaskManagementService
from core.notification_manager import NotificationManager
from core.scheduler import TaskScheduler
from handlers.task_handler import TaskHandler
from database.db_manager import DatabaseManager
from core.resource_manager import ResourceManager
from handlers.resource_handler import ResourceHandler

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Database
    db_manager = providers.Singleton(DatabaseManager)
    
    # Services
    notification_manager = providers.Singleton(NotificationManager, db=db_manager)
    task_service = providers.Singleton(
        TaskManagementService,
        db_manager=db_manager,
        notification_manager=notification_manager
    )
    
    # Schedulers
    task_scheduler = providers.Singleton(
        TaskScheduler,
        task_service=task_service
    )
    
    # Handlers
    task_handler = providers.Singleton(
        TaskHandler,
        task_service=task_service,
        notification_manager=notification_manager
    )
    
    # Resource Management
    resource_manager = providers.Singleton(
        ResourceManager,
        db_manager=db_manager,
        notification_manager=notification_manager
    )
    
    resource_handler = providers.Singleton(
        ResourceHandler,
        resource_manager=resource_manager,
        permission_manager=permission_manager
    )
