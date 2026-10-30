from __future__ import annotations
import math
import base64
import hashlib
import hmac
import secrets
import unicodedata

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4


if TYPE_CHECKING:
    from leaf_qt.security_audit import SecurityAuditOwner


LOCAL_PRINCIPAL_SCHEMA = "LEAF_LOCAL_PRINCIPAL_S1C_V1"
LOCAL_OS_SESSION = "LOCAL_OS_SESSION"
LOCAL_LOCKED = "LOCAL_LOCKED"

VALID_AUTHENTICATION_MODES = frozenset({
    LOCAL_OS_SESSION,
    LOCAL_LOCKED,
})

DEFAULT_AUTHENTICATION_MODE = (
    LOCAL_OS_SESSION
)


DEFAULT_INACTIVITY_TIMEOUT_SECONDS = 900.0


LOCAL_LOCKED_CREDENTIAL_SCHEMA = "LEAF_LOCAL_LOCKED_CREDENTIAL_S1L3_V1"
LOCAL_LOCKED_CREDENTIAL_FIELD = "local_locked_credential"
LOCAL_LOCKED_KDF = "SCRYPT_RFC7914"
LOCAL_LOCKED_MIN_LENGTH = 15
LOCAL_LOCKED_MAX_LENGTH = 256
LOCAL_LOCKED_SALT_BYTES = 16
LOCAL_LOCKED_DKLEN = 32
LOCAL_LOCKED_SCRYPT_N = 1 << 15
LOCAL_LOCKED_SCRYPT_R = 8
LOCAL_LOCKED_SCRYPT_P = 1
LOCAL_LOCKED_SCRYPT_MAXMEM = 64 * 1024 * 1024

LOCAL_RECOVERY_SCHEMA = "LEAF_LOCAL_PRINCIPAL_RECOVERY_S1O3_V1"
LOCAL_RECOVERY_ASSURANCE = "RECOVERY_CODE_HMAC_SHA256"
LOCAL_RECOVERY_PROOF_ALGORITHM = "HMAC_SHA256"
LOCAL_RECOVERY_CODE_BYTES = 32

LEAF_PUBLIC = "LEAF_PUBLIC"
LEAF_INTERNAL = "LEAF_INTERNAL"
LEAF_CONFIDENTIAL_ENGINEERING = "LEAF_CONFIDENTIAL_ENGINEERING"
LEAF_PERSONAL_DATA = "LEAF_PERSONAL_DATA"
LEAF_SECURITY_SECRET = "LEAF_SECURITY_SECRET"

VALID_SECURITY_CLASSIFICATIONS = frozenset({
    LEAF_PUBLIC,
    LEAF_INTERNAL,
    LEAF_CONFIDENTIAL_ENGINEERING,
    LEAF_PERSONAL_DATA,
    LEAF_SECURITY_SECRET,
})

DEFAULT_PROJECT_SECURITY_CLASSIFICATION = (
    LEAF_CONFIDENTIAL_ENGINEERING
)


def _coerce_inactivity_timeout_seconds(
    value: float,
) -> float:
    try:
        timeout = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "security_inactivity_timeout_invalid"
        ) from exc

    if (
        not math.isfinite(timeout)
        or
        timeout <= 0.0
    ):
        raise ValueError(
            "security_inactivity_timeout_invalid"
        )

    return timeout


class SecurityContextOwner:
    """Single owner of local principal identity and project access."""

    def __init__(
        self,
        principal_store_path: str | Path | None = None,
        security_audit: SecurityAuditOwner | None = None,
        inactivity_timeout_seconds: float = DEFAULT_INACTIVITY_TIMEOUT_SECONDS,
    ):
        self._inactivity_timeout_seconds = (
            _coerce_inactivity_timeout_seconds(
                inactivity_timeout_seconds
            )
        )

        self.principal_store_path = (
            Path(principal_store_path)
            if principal_store_path is not None
            else Path.home() / ".leaf/security/local_principal.json"
        )
        self._principal_id = None

        if security_audit is None:
            from leaf_qt.security_audit import SecurityAuditOwner

            security_audit_path = (
                None
                if principal_store_path is None
                else (
                    Path(principal_store_path).parent
                    / "security_audit.jsonl"
                )
            )

            security_audit = (
                SecurityAuditOwner(
                    security_audit_path
                )
            )

        self.security_audit = (
            security_audit
        )

    @property
    def principal_id(self) -> str:
        if self._principal_id is None:
            self._principal_id = self._load_or_create()
        return self._principal_id

    @property
    def authentication_mode(self) -> str:
        """
        Return the persisted authentication mode for the local
        principal.
        """
        return str(
            self
            ._read_local_principal_payload()
            .get(
                "authentication_mode",
                DEFAULT_AUTHENTICATION_MODE,
            )
        ).strip()


    @property
    def requires_explicit_unlock(self) -> bool:
        return (
            self.authentication_mode
            ==
            LOCAL_LOCKED
        )

    @property
    def is_authenticated(self) -> bool:
        return (
            bool(
                self.principal_id
            )
            and
            not self.requires_explicit_unlock
        )


    @staticmethod
    def _normalize_local_locked_credential(
        credential: str,
    ) -> str:
        if not isinstance(
            credential,
            str,
        ):
            raise TypeError(
                "local_locked_credential_must_be_string"
            )

        value = unicodedata.normalize(
            "NFC",
            credential,
        )

        if len(value) < LOCAL_LOCKED_MIN_LENGTH:
            raise ValueError(
                "local_locked_credential_too_short"
            )

        if len(value) > LOCAL_LOCKED_MAX_LENGTH:
            raise ValueError(
                "local_locked_credential_too_long"
            )

        return value

    @staticmethod
    def _derive_local_locked_credential_verifier(
        credential: str,
        *,
        salt: bytes,
    ) -> bytes:
        if len(salt) != LOCAL_LOCKED_SALT_BYTES:
            raise ValueError(
                "local_locked_credential_salt_invalid"
            )

        value = (
            SecurityContextOwner
            ._normalize_local_locked_credential(
                credential
            )
        )

        return hashlib.scrypt(
            value.encode("utf-8"),
            salt=salt,
            n=LOCAL_LOCKED_SCRYPT_N,
            r=LOCAL_LOCKED_SCRYPT_R,
            p=LOCAL_LOCKED_SCRYPT_P,
            maxmem=LOCAL_LOCKED_SCRYPT_MAXMEM,
            dklen=LOCAL_LOCKED_DKLEN,
        )

    def _read_local_principal_payload(
        self,
    ) -> dict[str, Any]:
        principal_id = self.principal_id

        payload = json.loads(
            self.principal_store_path.read_text(
                encoding="utf-8"
            )
        )

        mode = (
            str(
                payload.get(
                    "authentication_mode",
                    DEFAULT_AUTHENTICATION_MODE,
                )
            ).strip()
            if isinstance(payload, dict)
            else ""
        )

        if (
            not isinstance(payload, dict)
            or
            payload.get("schema")
            != LOCAL_PRINCIPAL_SCHEMA
            or
            payload.get("principal_id")
            != principal_id
            or
            mode
            not in VALID_AUTHENTICATION_MODES
        ):
            raise ValueError(
                "local_principal_record_invalid"
            )

        return payload

    def _write_local_principal_payload(
        self,
        payload: dict[str, Any],
    ) -> None:
        principal_id = self.principal_id

        mode = (
            str(
                payload.get(
                    "authentication_mode",
                    DEFAULT_AUTHENTICATION_MODE,
                )
            ).strip()
            if isinstance(payload, dict)
            else ""
        )

        if (
            not isinstance(payload, dict)
            or
            payload.get("schema")
            != LOCAL_PRINCIPAL_SCHEMA
            or
            payload.get("principal_id")
            != principal_id
            or
            mode
            not in VALID_AUTHENTICATION_MODES
        ):
            raise ValueError(
                "local_principal_record_invalid"
            )

        path = self.principal_store_path

        temporary = path.with_name(
            path.name
            + f".tmp-{os.getpid()}"
        )

        try:
            temporary.write_text(
                json.dumps(
                    payload,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            try:
                os.chmod(
                    temporary,
                    0o600,
                )
            except OSError:
                pass

            temporary.replace(
                path
            )

            try:
                os.chmod(
                    path,
                    0o600,
                )
            except OSError:
                pass

        except Exception:
            temporary.unlink(
                missing_ok=True
            )
            raise

    @property
    def has_local_locked_credential(
        self,
    ) -> bool:
        return isinstance(
            self
            ._read_local_principal_payload()
            .get(
                LOCAL_LOCKED_CREDENTIAL_FIELD
            ),
            dict,
        )

    def _build_local_locked_credential_record(
        self,
        credential: str,
    ) -> dict[str, Any]:
        value = (
            self
            ._normalize_local_locked_credential(
                credential
            )
        )

        salt = secrets.token_bytes(
            LOCAL_LOCKED_SALT_BYTES
        )

        verifier = (
            self
            ._derive_local_locked_credential_verifier(
                value,
                salt=salt,
            )
        )

        return {
            "schema":
                LOCAL_LOCKED_CREDENTIAL_SCHEMA,

            "kdf":
                LOCAL_LOCKED_KDF,

            "salt":
                base64.b64encode(
                    salt
                ).decode(
                    "ascii"
                ),

            "verifier":
                base64.b64encode(
                    verifier
                ).decode(
                    "ascii"
                ),

            "n":
                LOCAL_LOCKED_SCRYPT_N,

            "r":
                LOCAL_LOCKED_SCRYPT_R,

            "p":
                LOCAL_LOCKED_SCRYPT_P,

            "dklen":
                LOCAL_LOCKED_DKLEN,
        }

    def _install_local_locked_credential(
        self,
        credential: str,
    ) -> None:
        payload = (
            self
            ._read_local_principal_payload()
        )

        if isinstance(
            payload.get(
                LOCAL_LOCKED_CREDENTIAL_FIELD
            ),
            dict,
        ):
            raise FileExistsError(
                "local_locked_credential_"
                "already_configured"
            )

        record = (
            self
            ._build_local_locked_credential_record(
                credential
            )
        )

        path = self.principal_store_path
        original_bytes = path.read_bytes()

        original_mode = (
            (
                path.stat().st_mode
                &
                0o7777
            )
            if os.name == "posix"
            else None
        )

        payload[
            LOCAL_LOCKED_CREDENTIAL_FIELD
        ] = record

        try:
            self._write_local_principal_payload(
                payload
            )

            if not (
                self
                .verify_local_locked_credential(
                    credential
                )
            ):
                raise RuntimeError(
                    "local_locked_credential_"
                    "round_trip_failed"
                )

        except Exception:
            rollback = path.with_name(
                path.name
                +
                f".rollback-{os.getpid()}"
            )

            rollback.write_bytes(
                original_bytes
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        rollback,
                        original_mode,
                    )
                except OSError:
                    pass

            rollback.replace(
                path
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        path,
                        original_mode,
                    )
                except OSError:
                    pass

            raise


    def verify_local_locked_credential(
        self,
        credential: str,
    ) -> bool:
        try:
            value = (
                self
                ._normalize_local_locked_credential(
                    credential
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

        record = (
            self
            ._read_local_principal_payload()
            .get(
                LOCAL_LOCKED_CREDENTIAL_FIELD
            )
        )

        if not isinstance(
            record,
            dict,
        ):
            return False

        if (
            record.get("schema")
            != LOCAL_LOCKED_CREDENTIAL_SCHEMA
            or
            record.get("kdf")
            != LOCAL_LOCKED_KDF
            or
            record.get("n")
            != LOCAL_LOCKED_SCRYPT_N
            or
            record.get("r")
            != LOCAL_LOCKED_SCRYPT_R
            or
            record.get("p")
            != LOCAL_LOCKED_SCRYPT_P
            or
            record.get("dklen")
            != LOCAL_LOCKED_DKLEN
        ):
            raise ValueError(
                "local_locked_credential_"
                "record_invalid"
            )

        try:
            salt = base64.b64decode(
                record["salt"],
                validate=True,
            )

            expected = base64.b64decode(
                record["verifier"],
                validate=True,
            )

        except Exception as exc:
            raise ValueError(
                "local_locked_credential_"
                "record_invalid"
            ) from exc

        if (
            len(salt)
            != LOCAL_LOCKED_SALT_BYTES
            or
            len(expected)
            != LOCAL_LOCKED_DKLEN
        ):
            raise ValueError(
                "local_locked_credential_"
                "record_invalid"
            )

        actual = (
            self
            ._derive_local_locked_credential_verifier(
                value,
                salt=salt,
            )
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    def _record_local_authentication_event(
        self,
        *,
        action: str,
        outcome: str,
    ) -> None:
        self.security_audit.record_event(
            event_type="principal.authentication",
            action=action,
            outcome=outcome,
            resource_type="principal",
            principal_id=self.principal_id,
        )

    def enable_local_locked(
        self,
        credential: str,
    ) -> bool:
        """
        Enable LOCAL_LOCKED for the current local principal.

        The canonical principal is established before a
        transaction snapshot is taken.

        True:
            authentication mode changed.

        False:
            already LOCAL_LOCKED and supplied credential verified.
        """

        # The local principal is lazily created by the existing
        # security architecture. Force that canonical identity to
        # exist before taking the transaction snapshot.
        self.principal_id

        path = self.principal_store_path

        if not path.is_file():
            raise RuntimeError(
                "local_principal_store_not_created"
            )

        original_bytes = path.read_bytes()

        original_mode = (
            (
                path.stat().st_mode
                &
                0o7777
            )
            if os.name == "posix"
            else None
        )

        payload = (
            self
            ._read_local_principal_payload()
        )

        current_mode = str(
            payload.get(
                "authentication_mode",
                DEFAULT_AUTHENTICATION_MODE,
            )
        ).strip()

        if current_mode not in (
            LOCAL_OS_SESSION,
            LOCAL_LOCKED,
        ):
            raise ValueError(
                "local_authentication_mode_invalid"
            )

        # Idempotent already-locked case still requires proof of
        # the configured credential.
        if current_mode == LOCAL_LOCKED:

            if not (
                self
                .verify_local_locked_credential(
                    credential
                )
            ):
                self._record_local_authentication_event(
                    action="enable_locked",
                    outcome="denied",
                )

                raise PermissionError(
                    "local_locked_credential_invalid"
                )

            return False

        try:

            if self.has_local_locked_credential:

                if not (
                    self
                    .verify_local_locked_credential(
                        credential
                    )
                ):
                    self._record_local_authentication_event(
                        action="enable_locked",
                        outcome="denied",
                    )

                    raise PermissionError(
                        "local_locked_credential_invalid"
                    )

            else:

                try:
                    self._install_local_locked_credential(
                        credential
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    self._record_local_authentication_event(
                        action="enable_locked",
                        outcome="rejected",
                    )

                    raise

            payload = (
                self
                ._read_local_principal_payload()
            )

            payload[
                "authentication_mode"
            ] = LOCAL_LOCKED

            self._write_local_principal_payload(
                payload
            )

            if (
                self.authentication_mode
                != LOCAL_LOCKED
                or
                not self.has_local_locked_credential
                or
                not self
                .verify_local_locked_credential(
                    credential
                )
            ):
                raise RuntimeError(
                    "local_locked_activation_"
                    "verification_failed"
                )

            # Final accountability barrier.
            # Audit failure restores the complete original
            # local-principal record.
            self._record_local_authentication_event(
                action="enable_locked",
                outcome="success",
            )

        except Exception:

            rollback = path.with_name(
                path.name
                +
                f".rollback-{os.getpid()}"
            )

            rollback.write_bytes(
                original_bytes
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        rollback,
                        original_mode,
                    )
                except OSError:
                    pass

            rollback.replace(
                path
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        path,
                        original_mode,
                    )
                except OSError:
                    pass

            raise

        return True

    def change_local_locked_credential(
        self,
        current_credential: str,
        new_credential: str,
    ) -> bool:
        """
        Replace the LOCAL_LOCKED verifier after proving the
        current credential.
        """

        self.principal_id

        path = self.principal_store_path

        original_bytes = path.read_bytes()

        original_mode = (
            (
                path.stat().st_mode
                &
                0o7777
            )
            if os.name == "posix"
            else None
        )

        payload = (
            self
            ._read_local_principal_payload()
        )

        if (
            payload.get(
                "authentication_mode"
            )
            !=
            LOCAL_LOCKED
        ):
            self._record_local_authentication_event(
                action="change_credential",
                outcome="denied",
            )

            raise PermissionError(
                "local_locked_mode_required"
            )

        if not (
            self
            .verify_local_locked_credential(
                current_credential
            )
        ):
            self._record_local_authentication_event(
                action="change_credential",
                outcome="denied",
            )

            raise PermissionError(
                "local_locked_credential_invalid"
            )

        try:
            if (
                self
                .verify_local_locked_credential(
                    new_credential
                )
            ):
                self._record_local_authentication_event(
                    action="change_credential",
                    outcome="rejected",
                )

                raise ValueError(
                    "local_locked_credential_unchanged"
                )

            try:
                record = (
                    self
                    ._build_local_locked_credential_record(
                        new_credential
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                self._record_local_authentication_event(
                    action="change_credential",
                    outcome="rejected",
                )
                raise

            payload[
                LOCAL_LOCKED_CREDENTIAL_FIELD
            ] = record

            self._write_local_principal_payload(
                payload
            )

            if (
                not self
                .verify_local_locked_credential(
                    new_credential
                )
            ):
                raise RuntimeError(
                    "local_locked_credential_change_"
                    "verification_failed"
                )

            self._record_local_authentication_event(
                action="change_credential",
                outcome="success",
            )

        except Exception:
            # No mutation may survive a failed credential change.
            if (
                path.read_bytes()
                !=
                original_bytes
            ):
                rollback = path.with_name(
                    path.name
                    +
                    f".rollback-{os.getpid()}"
                )

                rollback.write_bytes(
                    original_bytes
                )

                if original_mode is not None:
                    try:
                        os.chmod(
                            rollback,
                            original_mode,
                        )
                    except OSError:
                        pass

                rollback.replace(
                    path
                )

                if original_mode is not None:
                    try:
                        os.chmod(
                            path,
                            original_mode,
                        )
                    except OSError:
                        pass

            raise

        return True

    def disable_local_locked(
        self,
        current_credential: str,
    ) -> bool:
        """
        Return to LOCAL_OS_SESSION after proving the current
        LOCAL_LOCKED credential.
        """

        self.principal_id

        path = self.principal_store_path

        original_bytes = path.read_bytes()

        original_mode = (
            (
                path.stat().st_mode
                &
                0o7777
            )
            if os.name == "posix"
            else None
        )

        payload = (
            self
            ._read_local_principal_payload()
        )

        current_mode = payload.get(
            "authentication_mode",
            DEFAULT_AUTHENTICATION_MODE,
        )

        if current_mode == LOCAL_OS_SESSION:
            if (
                LOCAL_LOCKED_CREDENTIAL_FIELD
                in payload
            ):
                raise RuntimeError(
                    "local_os_session_has_"
                    "unexpected_locked_credential"
                )

            return False

        if current_mode != LOCAL_LOCKED:
            raise ValueError(
                "local_authentication_mode_invalid"
            )

        if not (
            self
            .verify_local_locked_credential(
                current_credential
            )
        ):
            self._record_local_authentication_event(
                action="disable_locked",
                outcome="denied",
            )

            raise PermissionError(
                "local_locked_credential_invalid"
            )

        try:
            payload.pop(
                LOCAL_LOCKED_CREDENTIAL_FIELD,
                None,
            )

            payload[
                "authentication_mode"
            ] = LOCAL_OS_SESSION

            self._write_local_principal_payload(
                payload
            )

            if (
                self.authentication_mode
                !=
                LOCAL_OS_SESSION
                or
                self.has_local_locked_credential
                or
                not self.is_authenticated
            ):
                raise RuntimeError(
                    "local_locked_disable_"
                    "verification_failed"
                )

            self._record_local_authentication_event(
                action="disable_locked",
                outcome="success",
            )

        except Exception:
            rollback = path.with_name(
                path.name
                +
                f".rollback-{os.getpid()}"
            )

            rollback.write_bytes(
                original_bytes
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        rollback,
                        original_mode,
                    )
                except OSError:
                    pass

            rollback.replace(
                path
            )

            if original_mode is not None:
                try:
                    os.chmod(
                        path,
                        original_mode,
                    )
                except OSError:
                    pass

            raise

        return True

    @property
    def inactivity_timeout_seconds(
        self,
    ) -> float:
        """
        Return the canonical inactivity timeout policy.
        """
        return (
            self._inactivity_timeout_seconds
        )

    def initialise_runtime_security(
        self,
        session_lifecycle,
    ) -> str:
        """
        Apply the configured local authentication mode to an
        existing runtime session.

        Credential verification remains owned here; runtime owns
        only the resulting ephemeral state.
        """
        from leaf_qt.runtime.session_lifecycle import (
            RuntimeSessionLifecycle,
        )

        if not isinstance(
            session_lifecycle,
            RuntimeSessionLifecycle,
        ):
            raise TypeError(
                "runtime_session_lifecycle_required"
            )

        session = (
            session_lifecycle
            .require_session()
        )

        mode = self.authentication_mode

        if mode == LOCAL_LOCKED:
            session_lifecycle._lock_for_authentication()

            return "LOCKED"

        if mode == LOCAL_OS_SESSION:
            if not session.is_security_unlocked:
                raise RuntimeError(
                    "runtime_security_state_"
                    "inconsistent_with_local_os_session"
                )

            if (
                session.authenticated_principal_id
                is not None
            ):
                raise RuntimeError(
                    "runtime_os_session_has_"
                    "unexpected_authenticated_principal"
                )

            return "UNLOCKED"

        raise ValueError(
            "local_authentication_mode_invalid"
        )

    def unlock_runtime_session(
        self,
        credential: str,
        session_lifecycle,
    ) -> bool:
        """
        Verify the LOCAL_LOCKED credential and, only on success,
        commit the corresponding runtime-session unlock.
        """
        from leaf_qt.runtime.session_lifecycle import (
            RuntimeSessionLifecycle,
        )

        if not isinstance(
            session_lifecycle,
            RuntimeSessionLifecycle,
        ):
            raise TypeError(
                "runtime_session_lifecycle_required"
            )

        if (
            self.authentication_mode
            !=
            LOCAL_LOCKED
        ):
            raise RuntimeError(
                "local_locked_mode_required"
            )

        session = (
            session_lifecycle
            .require_session()
        )

        if session.is_security_unlocked:
            if (
                session.authenticated_principal_id
                ==
                self.principal_id
            ):
                return False

            raise RuntimeError(
                "runtime_security_session_not_locked"
            )

        try:
            verified = (
                self
                .verify_local_locked_credential(
                    credential
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            self._record_local_authentication_event(
                action="runtime_unlock",
                outcome="rejected",
            )

            raise

        if not verified:
            self._record_local_authentication_event(
                action="runtime_unlock",
                outcome="denied",
            )

            raise PermissionError(
                "local_locked_credential_invalid"
            )

        transition_performed = False

        try:
            transition_performed = (
                session_lifecycle
                ._complete_authenticated_unlock(
                    self.principal_id
                )
            )

            session = (
                session_lifecycle
                .require_session()
            )

            if (
                not session.is_security_unlocked
                or
                session.authenticated_principal_id
                !=
                self.principal_id
            ):
                raise RuntimeError(
                    "runtime_authenticated_unlock_"
                    "verification_failed"
                )

            self._record_local_authentication_event(
                action="runtime_unlock",
                outcome="success",
            )

        except Exception:
            if transition_performed:
                session_lifecycle._lock_for_authentication()

            raise

        return True

    def lock_runtime_session(
        self,
        session_lifecycle,
    ) -> bool:
        """
        Lock an authenticated LOCAL_LOCKED runtime session.

        No credential is required because this transition only
        reduces privilege.

        Audit failure never restores an unlocked session.
        """
        from leaf_qt.runtime.session_lifecycle import (
            RuntimeSessionLifecycle,
        )

        if not isinstance(
            session_lifecycle,
            RuntimeSessionLifecycle,
        ):
            raise TypeError(
                "runtime_session_lifecycle_required"
            )

        if (
            self.authentication_mode
            !=
            LOCAL_LOCKED
        ):
            raise RuntimeError(
                "local_locked_mode_required"
            )

        session = (
            session_lifecycle
            .require_session()
        )

        if session.is_security_locked:
            if (
                session.authenticated_principal_id
                is not None
            ):
                raise RuntimeError(
                    "runtime_locked_session_has_"
                    "authenticated_principal"
                )

            return False

        changed = (
            session_lifecycle
            ._lock_for_authentication()
        )

        session = (
            session_lifecycle
            .require_session()
        )

        if (
            not changed
            or
            not session.is_security_locked
            or
            session.authenticated_principal_id
            is not None
        ):
            raise RuntimeError(
                "runtime_security_lock_"
                "verification_failed"
            )

        # Deliberately do not roll back to UNLOCKED if audit
        # persistence fails. Remaining locked is the fail-closed
        # outcome.
        self._record_local_authentication_event(
            action="runtime_lock",
            outcome="success",
        )

        return True

    @property
    def default_project_classification(self) -> str:
        return DEFAULT_PROJECT_SECURITY_CLASSIFICATION

    def classification_for_project(self, project_manifest: Any) -> str:
        return (
            str(
                getattr(
                    project_manifest,
                    "security_classification",
                    DEFAULT_PROJECT_SECURITY_CLASSIFICATION,
                )
                or DEFAULT_PROJECT_SECURITY_CLASSIFICATION
            ).strip()
            or DEFAULT_PROJECT_SECURITY_CLASSIFICATION
        )

    def project_access_decision(
        self,
        project_manifest: Any,
        action: str = "access",
    ) -> dict[str, Any]:
        owner = str(
            getattr(
                project_manifest,
                "owner_principal_id",
                "",
            )
            or ""
        ).strip()

        legacy = not owner

        if legacy:
            allowed = action in {
                "access",
                "claim_legacy_project",
            }
            reason = (
                "legacy_unowned_project"
                if allowed
                else "legacy_project_claim_required"
            )
        elif action == "claim_legacy_project":
            allowed = False
            reason = "project_already_owned"
        else:
            allowed = owner == self.principal_id
            reason = (
                "owner_principal_match"
                if allowed
                else "owner_principal_mismatch"
            )

        return {
            "action": action,
            "allowed": allowed,
            "reason": reason,
            "legacy_unowned_project": legacy,
            "security_classification":
                self.classification_for_project(
                    project_manifest
                ),
        }

    def _project_runtime_session_decision(
        self,
    ) -> tuple[bool, str]:
        """
        Apply runtime authentication-session policy before
        protected project access, modification, or export.

        LOCAL_OS_SESSION preserves the existing authorization
        model. LOCAL_LOCKED fails closed unless the canonical
        runtime session is open, unlocked, and authenticated by
        this principal.
        """
        if (
            self.authentication_mode
            ==
            LOCAL_OS_SESSION
        ):
            return (
                True,
                "local_os_session",
            )

        if (
            self.authentication_mode
            !=
            LOCAL_LOCKED
        ):
            return (
                False,
                "authentication_mode_invalid",
            )

        from leaf_qt.runtime.session_lifecycle import (
            runtime_session_lifecycle,
        )

        try:
            session = (
                runtime_session_lifecycle
                .require_session()
            )

        except RuntimeError as exc:
            if (
                str(exc)
                ==
                "runtime_session_not_open"
            ):
                return (
                    False,
                    "runtime_session_not_open",
                )

            raise

        if session.is_security_locked:
            return (
                False,
                "runtime_session_locked",
            )

        if (
            session.authenticated_principal_id
            !=
            self.principal_id
        ):
            return (
                False,
                "runtime_session_principal_mismatch",
            )

        return (
            True,
            "runtime_session_authenticated",
        )

    def can_access_project(
        self,
        project_manifest: Any,
    ) -> bool:
        session_allowed, _ = (
            self
            ._project_runtime_session_decision()
        )

        if not session_allowed:
            return False

        return self.project_access_decision(
            project_manifest,
            "access",
        )["allowed"]


    def can_modify_project(
        self,
        project_manifest: Any,
    ) -> bool:
        session_allowed, _ = (
            self
            ._project_runtime_session_decision()
        )

        if not session_allowed:
            return False

        return self.project_access_decision(
            project_manifest,
            "modify",
        )["allowed"]


    def can_export_project(
        self,
        project_manifest: Any,
    ) -> bool:
        session_allowed, _ = (
            self
            ._project_runtime_session_decision()
        )

        if not session_allowed:
            return False

        return self.project_access_decision(
            project_manifest,
            "export",
        )["allowed"]


    def require_project_access(self, project_manifest: Any) -> None:
        self._require(project_manifest, "access")

    def require_project_modify(self, project_manifest: Any) -> None:
        self._require(project_manifest, "modify")

    def require_project_export(self, project_manifest: Any) -> None:
        self._require(project_manifest, "export")

    def require_legacy_project_claim(
        self,
        project_manifest: Any,
    ) -> None:
        self._require(project_manifest, "claim_legacy_project")

    def _record_project_ownership(
        self,
        *,
        outcome: str,
        project_id: str | None = None,
        classification: str | None = None,
    ) -> None:
        self.security_audit.record_event(
            event_type="project.ownership",
            action="bind",
            outcome=outcome,
            resource_type="project",
            classification=classification,
            principal_id=self.principal_id,
            project_id=project_id,
        )

    def bind_new_project(self, project_manifest: Any) -> Any:
        project_id = str(
            getattr(
                project_manifest,
                "project_id",
                "",
            )
            or ""
        ).strip()

        audit_project_id = (
            project_id
            if project_id.startswith(
                "project_"
            )
            else None
        )

        owner = str(
            getattr(
                project_manifest,
                "owner_principal_id",
                "",
            )
            or ""
        ).strip()

        if owner and owner != self.principal_id:
            self._record_project_ownership(
                outcome="denied",
                project_id=audit_project_id,
            )

            raise PermissionError(
                "project_owner_principal_conflict"
            )

        classification = self.classification_for_project(
            project_manifest
        )

        if classification not in VALID_SECURITY_CLASSIFICATIONS:
            self._record_project_ownership(
                outcome="failure",
                project_id=audit_project_id,
            )

            raise ValueError(
                "project_security_classification_invalid"
            )

        previous_owner = getattr(
            project_manifest,
            "owner_principal_id",
            "",
        )

        previous_classification = getattr(
            project_manifest,
            "security_classification",
            "",
        )

        project_manifest.owner_principal_id = (
            self.principal_id
        )

        project_manifest.security_classification = (
            classification
        )

        try:
            self._record_project_ownership(
                outcome="success",
                project_id=audit_project_id,
                classification=classification,
            )

        except Exception:
            project_manifest.owner_principal_id = (
                previous_owner
            )

            project_manifest.security_classification = (
                previous_classification
            )

            raise

        return project_manifest

    def _record_project_authorization(
        self,
        project_manifest: Any,
        action: str,
        allowed: bool,
    ) -> None:
        project_id = str(
            getattr(
                project_manifest,
                "project_id",
                "",
            )
            or ""
        ).strip()

        self.security_audit.record_event(
            event_type=
                "project.authorization",
            action=
                action,
            outcome=
                (
                    "success"
                    if allowed
                    else "denied"
                ),
            resource_type=
                "project",
            classification=
                self.classification_for_project(
                    project_manifest
                ),
            principal_id=
                self.principal_id,
            project_id=
                (
                    project_id
                    or None
                ),
        )

    def _require(
        self,
        project_manifest: Any,
        action: str,
    ) -> None:
        session_allowed, session_reason = (
            self
            ._project_runtime_session_decision()
        )

        if session_allowed:
            decision = self.project_access_decision(
                project_manifest,
                action,
            )

        else:
            decision = {
                "allowed":
                    False,

                "reason":
                    session_reason,
            }

        self._record_project_authorization(
            project_manifest,
            action,
            bool(
                decision["allowed"]
            ),
        )

        if not decision["allowed"]:
            raise PermissionError(
                "project_access_denied:"
                f"{action}:"
                f"{decision['reason']}"
            )


    def _record_device_trust(self, action: str, outcome: str) -> None:
        self.security_audit.record_event(
            event_type="device.trust", action=action, outcome=outcome,
            resource_type="device_trust", principal_id=self.principal_id,
        )

    def _require_device_trust_session(self, action: str) -> None:
        allowed, reason = self._project_runtime_session_decision()
        if not allowed:
            self._record_device_trust(action, "denied")
            raise PermissionError(f"device_trust_denied:{action}:{reason}")

    def _device_trust_custody(self, key_custody=None):
        if key_custody is not None:
            return key_custody
        from leaf_qt.key_custody import KeyCustodyOwner
        return KeyCustodyOwner(security_audit=self.security_audit)

    def enroll_trusted_device(self, key_custody=None) -> bool:
        self._require_device_trust_session("enroll")
        try:
            changed = self._device_trust_custody(key_custody).enroll_device_trust(
                self.principal_id
            )
        except Exception:
            self._record_device_trust("enroll", "failure")
            raise
        self._record_device_trust("enroll", "success")
        return changed

    def require_trusted_device(self, key_custody=None) -> None:
        self._require_device_trust_session("require")
        try:
            trusted = self._device_trust_custody(key_custody).device_trust_exists(
                self.principal_id
            )
        except Exception:
            self._record_device_trust("require", "failure")
            raise
        if not trusted:
            self._record_device_trust("require", "denied")
            raise PermissionError("trusted_device_required")
        self._record_device_trust("require", "success")

    def recovery_boundary(self) -> dict[str, object]:
        return {
            "schema": LOCAL_RECOVERY_SCHEMA,
            "assurance": LOCAL_RECOVERY_ASSURANCE,
            "portable_local_recovery": True,
            "cryptographic_identity_proof": True,
            "proof_algorithm": LOCAL_RECOVERY_PROOF_ALGORITHM,
            "separate_recovery_code": True,
            "recovery_code_stored_in_record": False,
            "password_recovery": False,
            "email_recovery": False,
            "cloud_recovery": False,
            "automatic_principal_reassignment": False,
        }

    @staticmethod
    def _record_local_principal_recovery(
        security_audit: Any,
        *,
        action: str,
        outcome: str,
        principal_id: str | None = None,
    ) -> None:
        security_audit.record_event(
            event_type="principal.recovery",
            action=action,
            outcome=outcome,
            resource_type="principal",
            principal_id=principal_id,
        )

    @staticmethod
    def _principal_recovery_code_key(recovery_code: str) -> bytes:
        value = recovery_code.strip() if isinstance(recovery_code, str) else ""
        try:
            key = bytes.fromhex(value)
        except ValueError as exc:
            raise ValueError("principal_recovery_code_invalid") from exc
        if len(value) != LOCAL_RECOVERY_CODE_BYTES * 2 or len(key) != LOCAL_RECOVERY_CODE_BYTES:
            raise ValueError("principal_recovery_code_invalid")
        return key

    @classmethod
    def _principal_recovery_proof(
        cls,
        payload: dict[str, Any],
        recovery_code: str,
    ) -> str:
        fields = (
            "schema", "principal_id", "authentication_mode", "assurance",
            "cryptographic_identity_proof", "proof_algorithm",
        )
        message = json.dumps(
            {key: payload.get(key) for key in fields},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hmac.new(
            cls._principal_recovery_code_key(recovery_code),
            message,
            hashlib.sha256,
        ).hexdigest()

    def export_recovery_record(
        self,
        destination: str | Path,
        overwrite: bool = False,
    ) -> tuple[Path, str]:
        destination = Path(destination)

        destination_preexisting = (
            destination.exists()
        )

        previous_bytes = (
            destination.read_bytes()
            if destination_preexisting
            else None
        )

        previous_mode = (
            (
                destination.stat().st_mode
                &
                0o7777
            )
            if (
                destination_preexisting
                and
                os.name == "posix"
            )
            else None
        )

        if (
            destination_preexisting
            and
            not overwrite
        ):
            self._record_local_principal_recovery(
                self.security_audit,
                action="export",
                outcome="failure",
                principal_id=self.principal_id,
            )

            raise FileExistsError(
                "principal_recovery_record_exists:"
                f"{destination}"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        principal_id = (
            self.principal_id
        )

        recovery_code = secrets.token_hex(LOCAL_RECOVERY_CODE_BYTES)
        payload = {
            "schema": LOCAL_RECOVERY_SCHEMA,
            "principal_id": principal_id,
            "authentication_mode": DEFAULT_AUTHENTICATION_MODE,
            "assurance": LOCAL_RECOVERY_ASSURANCE,
            "cryptographic_identity_proof": True,
            "proof_algorithm": LOCAL_RECOVERY_PROOF_ALGORITHM,
        }
        payload["proof"] = self._principal_recovery_proof(payload, recovery_code)

        temporary = destination.with_name(
            destination.name
            +
            f".tmp-{os.getpid()}"
        )

        try:
            temporary.write_text(
                json.dumps(
                    payload,
                    indent=2,
                )
                +
                "\n",
                encoding="utf-8",
            )

            try:
                os.chmod(
                    temporary,
                    0o600,
                )

            except OSError:
                pass

            temporary.replace(
                destination
            )

            try:
                os.chmod(
                    destination,
                    0o600,
                )

            except OSError:
                pass

        except Exception:
            temporary.unlink(
                missing_ok=True
            )

            self._record_local_principal_recovery(
                self.security_audit,
                action="export",
                outcome="failure",
                principal_id=principal_id,
            )

            raise

        try:
            self._record_local_principal_recovery(
                self.security_audit,
                action="export",
                outcome="success",
                principal_id=principal_id,
            )

        except Exception:
            if destination_preexisting:
                rollback = destination.with_name(
                    destination.name
                    +
                    f".audit-rollback-{os.getpid()}"
                )

                rollback.write_bytes(
                    previous_bytes
                )

                if previous_mode is not None:
                    try:
                        os.chmod(
                            rollback,
                            previous_mode,
                        )

                    except OSError:
                        pass

                rollback.replace(
                    destination
                )

                if previous_mode is not None:
                    try:
                        os.chmod(
                            destination,
                            previous_mode,
                        )

                    except OSError:
                        pass

                if (
                    destination.read_bytes()
                    !=
                    previous_bytes
                ):
                    raise RuntimeError(
                        "principal_recovery_export_"
                        "audit_rollback_failed"
                    )

            else:
                destination.unlink(
                    missing_ok=True
                )

            raise

        return destination, recovery_code


    @classmethod
    def restore_recovery_record(
        cls,
        recovery_record_path: str | Path,
        recovery_code: str,
        principal_store_path: str | Path | None = None,
        security_audit: Any = None,
    ) -> "SecurityContextOwner":
        if security_audit is None:
            from leaf_qt.security_audit import SecurityAuditOwner

            security_audit = SecurityAuditOwner()

        recovery_record_path = Path(
            recovery_record_path
        )

        try:
            payload = json.loads(
                recovery_record_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="failure",
            )

            raise

        principal_id = str(
            payload.get(
                "principal_id",
                "",
            )
        ).strip()

        proof = str(payload.get("proof", "")).strip()
        if (
            payload.get("schema") != LOCAL_RECOVERY_SCHEMA
            or payload.get("assurance") != LOCAL_RECOVERY_ASSURANCE
            or payload.get("authentication_mode") != DEFAULT_AUTHENTICATION_MODE
            or payload.get("cryptographic_identity_proof") is not True
            or payload.get("proof_algorithm") != LOCAL_RECOVERY_PROOF_ALGORITHM
            or len(proof) != hashlib.sha256().digest_size * 2
            or not principal_id.startswith("principal_")
        ):
            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="rejected",
            )
            raise ValueError("principal_recovery_record_invalid")

        try:
            expected_proof = cls._principal_recovery_proof(payload, recovery_code)
        except ValueError as exc:
            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="rejected",
                principal_id=principal_id,
            )
            raise PermissionError("principal_recovery_proof_invalid") from exc

        if not hmac.compare_digest(expected_proof, proof):
            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="rejected",
                principal_id=principal_id,
            )
            raise PermissionError("principal_recovery_proof_invalid")

        destination = (
            Path(
                principal_store_path
            )
            if principal_store_path
            is not None
            else
            (
                Path.home()
                / ".leaf"
                / "security"
                / "local_principal.json"
            )
        )

        if destination.exists():
            try:
                existing_payload = json.loads(
                    destination.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:
                cls._record_local_principal_recovery(
                    security_audit,
                    action="restore",
                    outcome="failure",
                    principal_id=principal_id,
                )

                raise

            existing_id = str(
                existing_payload.get(
                    "principal_id",
                    "",
                )
            ).strip()

            if (
                existing_payload.get(
                    "schema"
                )
                ==
                LOCAL_PRINCIPAL_SCHEMA
                and
                existing_id
                ==
                principal_id
            ):
                restored = cls(
                    destination,
                    security_audit=
                        security_audit,
                )

                cls._record_local_principal_recovery(
                    security_audit,
                    action="restore",
                    outcome="success",
                    principal_id=principal_id,
                )

                return restored

            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="denied",
                principal_id=principal_id,
            )

            raise PermissionError(
                "principal_recovery_destination_conflict"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = destination.with_name(
            destination.name
            +
            f".tmp-{os.getpid()}"
        )

        destination_created = False

        try:
            temporary.write_text(
                json.dumps(
                    {
                        "schema":
                            LOCAL_PRINCIPAL_SCHEMA,

                        "principal_id":
                            principal_id,

                        "authentication_mode":
                            DEFAULT_AUTHENTICATION_MODE,
                    },
                    indent=2,
                )
                +
                "\n",
                encoding="utf-8",
            )

            try:
                os.chmod(
                    temporary,
                    0o600,
                )

            except OSError:
                pass

            temporary.replace(
                destination
            )

            destination_created = True

            try:
                os.chmod(
                    destination,
                    0o600,
                )

            except OSError:
                pass

            restored = cls(
                destination,
                security_audit=
                    security_audit,
            )

            if (
                restored.principal_id
                !=
                principal_id
            ):
                raise RuntimeError(
                    "principal_recovery_"
                    "verification_failed"
                )

        except Exception:
            temporary.unlink(
                missing_ok=True
            )

            if destination_created:
                destination.unlink(
                    missing_ok=True
                )

            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="failure",
                principal_id=principal_id,
            )

            raise

        try:
            cls._record_local_principal_recovery(
                security_audit,
                action="restore",
                outcome="success",
                principal_id=principal_id,
            )

        except Exception:
            destination.unlink(
                missing_ok=True
            )

            raise

        return restored


    def _load_or_create(self) -> str:
        path = self.principal_store_path

        if path.exists():
            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            principal_id = str(
                payload.get(
                    "principal_id",
                    "",
                )
            ).strip()

            if (
                payload.get("schema")
                != LOCAL_PRINCIPAL_SCHEMA
                or
                not principal_id.startswith(
                    "principal_"
                )
            ):
                raise ValueError(
                    "local_principal_record_invalid"
                )

            return principal_id

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            os.chmod(
                path.parent,
                0o700,
            )
        except OSError:
            pass

        principal_id = (
            "principal_"
            + uuid4().hex
        )

        temporary = path.with_name(
            path.name
            + f".tmp-{os.getpid()}"
        )

        temporary.write_text(
            json.dumps(
                {
                    "schema":
                        LOCAL_PRINCIPAL_SCHEMA,
                    "principal_id":
                        principal_id,
                    "authentication_mode":
                        DEFAULT_AUTHENTICATION_MODE,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        try:
            os.chmod(
                temporary,
                0o600,
            )
        except OSError:
            pass

        temporary.replace(path)

        try:
            os.chmod(
                path,
                0o600,
            )
        except OSError:
            pass

        return principal_id
