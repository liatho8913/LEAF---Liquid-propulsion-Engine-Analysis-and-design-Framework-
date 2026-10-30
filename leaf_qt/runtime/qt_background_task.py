"""Canonical reusable Qt background-callable execution owner.

Infrastructure only.

Engineering owners supply callables.
GUI owners receive completion/failure signals on the Qt main thread.
"""

from __future__ import annotations

import traceback

from PySide6.QtCore import (
    QObject,
    QRunnable,
    QThreadPool,
    Signal,
    Slot,
)


class _QtBackgroundTaskSignals(QObject):
    completed = Signal(object)
    failed = Signal(str)
    finished = Signal()


class _QtBackgroundTaskRunnable(QRunnable):
    def __init__(
        self,
        callable_owner,
        args,
        kwargs,
    ):
        super().__init__()

        self._callable_owner = (
            callable_owner
        )

        self._args = tuple(
            args
        )

        self._kwargs = dict(
            kwargs
        )

        self.signals = (
            _QtBackgroundTaskSignals()
        )

        self.setAutoDelete(
            True
        )

    @Slot()
    def run(self):
        try:
            result = (
                self._callable_owner(
                    *self._args,
                    **self._kwargs,
                )
            )

            self.signals.completed.emit(
                result
            )

        except Exception:
            self.signals.failed.emit(
                traceback.format_exc()
            )

        finally:
            self.signals.finished.emit()


class QtBackgroundTaskOwner(QObject):
    """Own one reusable non-blocking Qt callable execution."""

    started = Signal(str)
    completed = Signal(object)
    failed = Signal(str)
    finished = Signal(str)

    def __init__(
        self,
        parent=None,
        thread_pool=None,
    ):
        super().__init__(
            parent
        )

        self._thread_pool = (
            thread_pool
            or
            QThreadPool.globalInstance()
        )

        self._running = False
        self._task_name = ""
        self._runnable = None

    @property
    def running(self):
        return bool(
            self._running
        )

    @property
    def task_name(self):
        return str(
            self._task_name
            or
            ""
        )

    def start(
        self,
        task_name,
        callable_owner,
        *args,
        **kwargs,
    ):
        if self._running:
            return False

        if not callable(
            callable_owner
        ):
            raise TypeError(
                "Background task callable must be callable."
            )

        self._task_name = str(
            task_name
            or
            "background_task"
        )

        runnable = (
            _QtBackgroundTaskRunnable(
                callable_owner,
                args,
                kwargs,
            )
        )

        runnable.signals.completed.connect(
            self._relay_completed
        )

        runnable.signals.failed.connect(
            self._relay_failed
        )

        runnable.signals.finished.connect(
            self._relay_finished
        )

        self._runnable = runnable
        self._running = True

        self.started.emit(
            self._task_name
        )

        self._thread_pool.start(
            runnable
        )

        return True

    @Slot(object)
    def _relay_completed(
        self,
        result,
    ):
        self.completed.emit(
            result
        )

    @Slot(str)
    def _relay_failed(
        self,
        error_text,
    ):
        self.failed.emit(
            str(
                error_text
                or
                "Background task failed."
            )
        )

    @Slot()
    def _relay_finished(
        self,
    ):
        task_name = (
            self._task_name
        )

        self._running = False
        self._runnable = None

        self.finished.emit(
            task_name
        )
