from __future__ import annotations

import importlib.util
import sys
from dataclasses import asdict, dataclass

from PySide6.QtCore import QSysInfo


SCHEMA = "LEAF_PLATFORM_CAPABILITIES_S1F_V1"


@dataclass(frozen=True)
class PlatformCapabilities:
    os_family: str
    os_version: str
    kernel_type: str
    kernel_version: str
    current_cpu_architecture: str
    build_cpu_architecture: str
    build_abi: str
    secret_store_backend: str
    secret_store_available: bool
    secure_authentication_capabilities: tuple[str, ...]

    def snapshot(self) -> dict[str, object]:
        payload = asdict(self)
        payload["schema"] = SCHEMA
        return payload


class PlatformCapabilityOwner:
    """
    Canonical owner of host-platform capability detection.

    Engineering physics/modules, storage and GUI surfaces
    consume this contract instead of independently deciding
    what operating system LEAF is running on.
    """

    SECRET_STORE_BACKENDS = {
        "macos": "APPLE_KEYCHAIN",
        "windows": "WINDOWS_CREDENTIAL_LOCKER",
        "linux": "FREEDESKTOP_SECRET_SERVICE_OR_KWALLET",
        "unsupported": "UNSUPPORTED",
    }

    SUPPORTED_DESKTOP_FAMILIES = frozenset({
        "macos",
        "windows",
        "linux",
    })

    @staticmethod
    def family_for_sys_platform(value: str) -> str:
        value = str(value or "").lower()

        if value == "darwin":
            return "macos"

        if value in {
            "win32",
            "cygwin",
            "msys",
        }:
            return "windows"

        if value.startswith("linux"):
            return "linux"

        return "unsupported"

    @property
    def os_family(self) -> str:
        return self.family_for_sys_platform(
            sys.platform
        )

    @property
    def supported(self) -> bool:
        return (
            self.os_family
            in
            self.SUPPORTED_DESKTOP_FAMILIES
        )

    def detect(self) -> PlatformCapabilities:
        family = self.os_family

        return PlatformCapabilities(
            os_family=family,

            os_version=str(
                QSysInfo.productVersion()
                or
                QSysInfo.kernelVersion()
                or
                "unknown"
            ),

            kernel_type=str(
                QSysInfo.kernelType()
                or
                "unknown"
            ),

            kernel_version=str(
                QSysInfo.kernelVersion()
                or
                "unknown"
            ),

            current_cpu_architecture=str(
                QSysInfo.currentCpuArchitecture()
                or
                "unknown"
            ),

            build_cpu_architecture=str(
                QSysInfo.buildCpuArchitecture()
                or
                "unknown"
            ),

            build_abi=str(
                QSysInfo.buildAbi()
                or
                "unknown"
            ),

            secret_store_backend=(
                self.SECRET_STORE_BACKENDS[
                    family
                ]
            ),

            secret_store_available=(
                family
                in
                self.SUPPORTED_DESKTOP_FAMILIES
                and
                importlib.util.find_spec(
                    "keyring"
                )
                is not None
            ),

            secure_authentication_capabilities=(
                "LOCAL_OS_SESSION",
            ),
        )

    def snapshot(self) -> dict[str, object]:
        return self.detect().snapshot()
