"""Code locator module - the main interface for LocAgent."""

from .locator import CodeLocator
from .tools import setup_localization_tools

__all__ = ['CodeLocator', 'setup_localization_tools']