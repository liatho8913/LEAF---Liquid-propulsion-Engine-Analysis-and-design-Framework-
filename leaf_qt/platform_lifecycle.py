from __future__ import annotations

import ctypes
import weakref

from PySide6.QtCore import (
    QAbstractNativeEventFilter,
    QCoreApplication,
    QObject,
    SLOT,
    Signal,
    Slot,
)

from leaf_qt.platform_capabilities import PlatformCapabilityOwner


class PlatformLifecycleOwner(QObject):
    """Canonical owner of operating-system lifecycle observation."""

    restrictive_event = Signal(str)

    EVENT_SLEEP = "SLEEP"
    EVENT_WAKE = "WAKE"

    BACKEND_MACOS_NS_WORKSPACE = "MACOS_NS_WORKSPACE"
    BACKEND_WINDOWS_POWER_BROADCAST = "WINDOWS_POWER_BROADCAST"
    BACKEND_LINUX_LOGIND = "LINUX_LOGIND"

    WINDOWS_WM_POWERBROADCAST = 0x0218
    WINDOWS_PBT_APMSUSPEND = 0x0004
    WINDOWS_PBT_APMRESUMEAUTOMATIC = 0x0012

    LINUX_LOGIND_SERVICE = "org.freedesktop.login1"
    LINUX_LOGIND_PATH = "/org/freedesktop/login1"
    LINUX_LOGIND_INTERFACE = "org.freedesktop.login1.Manager"
    LINUX_PREPARE_FOR_SLEEP = "PrepareForSleep"

    def __init__(
        self,
        capability_owner: PlatformCapabilityOwner | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._capability_owner = capability_owner or PlatformCapabilityOwner()
        self._started = False
        self._backend = None

        self._notification_centre = None
        self._observer_tokens = ()
        self._observer_blocks = ()

        self._native_event_application = None
        self._native_event_filter = None

        self._dbus_connection = None
        self._dbus_slot = None

    @property
    def os_family(self) -> str:
        return self._capability_owner.os_family

    @property
    def started(self) -> bool:
        return self._started

    @property
    def backend(self) -> str | None:
        return self._backend

    def start(self) -> bool:
        if self._started:
            return False

        starter = {
            "macos": self._start_macos,
            "windows": self._start_windows,
            "linux": self._start_linux,
        }.get(self.os_family)

        return starter() if starter is not None else False

    def stop(self) -> bool:
        if not self._started:
            return False

        first_error = None

        try:
            if self._backend == self.BACKEND_MACOS_NS_WORKSPACE:
                for token in tuple(self._observer_tokens):
                    try:
                        self._notification_centre.removeObserver_(
                            token
                        )
                    except Exception as exc:
                        if first_error is None:
                            first_error = exc

            elif self._backend == self.BACKEND_WINDOWS_POWER_BROADCAST:
                try:
                    self._native_event_application.removeNativeEventFilter(
                        self._native_event_filter
                    )
                except Exception as exc:
                    first_error = exc

            elif self._backend == self.BACKEND_LINUX_LOGIND:
                try:
                    disconnected = self._dbus_connection.disconnect(
                        self.LINUX_LOGIND_SERVICE,
                        self.LINUX_LOGIND_PATH,
                        self.LINUX_LOGIND_INTERFACE,
                        self.LINUX_PREPARE_FOR_SLEEP,
                        self,
                        self._dbus_slot,
                    )

                    if not disconnected:
                        first_error = RuntimeError(
                            "linux_prepare_for_sleep_disconnect_failed"
                        )

                except Exception as exc:
                    first_error = exc

        finally:
            self._started = False
            self._backend = None

            self._notification_centre = None
            self._observer_tokens = ()
            self._observer_blocks = ()

            self._native_event_application = None
            self._native_event_filter = None

            self._dbus_connection = None
            self._dbus_slot = None

        if first_error is not None:
            raise first_error

        return True

    def _start_macos(self) -> bool:
        try:
            from AppKit import (
                NSWorkspace,
                NSWorkspaceDidWakeNotification,
                NSWorkspaceWillSleepNotification,
            )

        except ImportError:
            return False

        notification_centre = (
            NSWorkspace
            .sharedWorkspace()
            .notificationCenter()
        )

        if notification_centre is None:
            raise RuntimeError(
                "macos_workspace_notification_center_unavailable"
            )

        owner_reference = weakref.ref(
            self
        )
        sleep_event = self.EVENT_SLEEP
        wake_event = self.EVENT_WAKE

        def emit(event: str) -> None:
            owner = owner_reference()

            if owner is not None:
                owner.restrictive_event.emit(
                    event
                )

        def emit_sleep(notification):
            emit(
                sleep_event
            )

        def emit_wake(notification):
            emit(
                wake_event
            )

        sleep_token = (
            notification_centre
            .addObserverForName_object_queue_usingBlock_(
                NSWorkspaceWillSleepNotification,
                None,
                None,
                emit_sleep,
            )
        )

        try:
            wake_token = (
                notification_centre
                .addObserverForName_object_queue_usingBlock_(
                    NSWorkspaceDidWakeNotification,
                    None,
                    None,
                    emit_wake,
                )
            )

        except Exception:
            notification_centre.removeObserver_(
                sleep_token
            )
            raise

        self._notification_centre = (
            notification_centre
        )
        self._observer_tokens = (
            sleep_token,
            wake_token,
        )
        self._observer_blocks = (
            emit_sleep,
            emit_wake,
        )
        self._backend = (
            self.BACKEND_MACOS_NS_WORKSPACE
        )
        self._started = True

        return True

    def _start_windows(self) -> bool:
        try:
            from ctypes import wintypes

        except ImportError:
            return False

        application = (
            QCoreApplication.instance()
        )

        if application is None:
            raise RuntimeError(
                "windows_qt_application_unavailable"
            )

        owner_reference = weakref.ref(
            self
        )
        message_type = wintypes.MSG

        class WindowsPowerEventFilter(
            QAbstractNativeEventFilter
        ):
            def nativeEventFilter(
                filter_self,
                event_type,
                message,
            ):
                if bytes(event_type) not in {
                    b"windows_generic_MSG",
                    b"windows_dispatcher_MSG",
                }:
                    return False

                owner = owner_reference()

                if owner is None:
                    return False

                native_message = ctypes.cast(
                    ctypes.c_void_p(int(message)),
                    ctypes.POINTER(
                        message_type
                    ),
                ).contents

                owner._handle_windows_power_event(
                    int(
                        native_message.message
                    ),
                    int(
                        native_message.wParam
                    ),
                )

                return False

        event_filter = (
            WindowsPowerEventFilter()
        )

        application.installNativeEventFilter(
            event_filter
        )

        self._native_event_application = (
            application
        )
        self._native_event_filter = (
            event_filter
        )
        self._backend = (
            self.BACKEND_WINDOWS_POWER_BROADCAST
        )
        self._started = True

        return True

    def _handle_windows_power_event(
        self,
        message_id: int,
        power_event: int,
    ) -> None:
        if (
            message_id
            !=
            self.WINDOWS_WM_POWERBROADCAST
        ):
            return

        if (
            power_event
            ==
            self.WINDOWS_PBT_APMSUSPEND
        ):
            self.restrictive_event.emit(
                self.EVENT_SLEEP
            )

        elif (
            power_event
            ==
            self.WINDOWS_PBT_APMRESUMEAUTOMATIC
        ):
            self.restrictive_event.emit(
                self.EVENT_WAKE
            )

    def _start_linux(self) -> bool:
        try:
            from PySide6.QtDBus import (
                QDBusConnection,
                QDBusInterface,
            )

        except ImportError:
            return False

        connection = (
            QDBusConnection.systemBus()
        )

        if not connection.isConnected():
            return False

        interface = QDBusInterface(
            self.LINUX_LOGIND_SERVICE,
            self.LINUX_LOGIND_PATH,
            self.LINUX_LOGIND_INTERFACE,
            connection,
        )

        if not interface.isValid():
            return False

        slot = SLOT(
            "_handle_linux_prepare_for_sleep(bool)"
        )

        connected = connection.connect(
            self.LINUX_LOGIND_SERVICE,
            self.LINUX_LOGIND_PATH,
            self.LINUX_LOGIND_INTERFACE,
            self.LINUX_PREPARE_FOR_SLEEP,
            self,
            slot,
        )

        if not connected:
            return False

        self._dbus_connection = (
            connection
        )
        self._dbus_slot = slot
        self._backend = (
            self.BACKEND_LINUX_LOGIND
        )
        self._started = True

        return True

    @Slot(bool)
    def _handle_linux_prepare_for_sleep(
        self,
        preparing_for_sleep: bool,
    ) -> None:
        self.restrictive_event.emit(
            self.EVENT_SLEEP
            if preparing_for_sleep
            else
            self.EVENT_WAKE
        )
