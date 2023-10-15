from __future__ import annotations
from dependency_injector import containers, providers

from flowtutor.codegenerator import CodeGenerator
from flowtutor.modal_service import ModalService
from flowtutor.util_service import UtilService
from flowtutor.settings_service import SettingsService
from flowtutor.language_service import LanguageService


class Container(containers.DeclarativeContainer):
    '''The container for dependency injection.'''

    utils_service = providers.Singleton(
        UtilService
    )

    code_generator = providers.Singleton(
        CodeGenerator
    )

    modal_service = providers.Singleton(
        ModalService
    )

    settings_service = providers.Singleton(
        SettingsService
    )

    language_service = providers.Singleton(
        LanguageService
    )
