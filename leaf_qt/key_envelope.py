from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import (
    InvalidUnwrap,
    aes_key_unwrap,
    aes_key_wrap,
)


SCHEMA = "LEAF_PORTABLE_KEY_ENVELOPE_S1H_V1"

RECOVERY_KEY_PREFIX = "LEAF-RK1-"

RECOVERY_KEY_BYTES = 32
PROJECT_KEY_BYTES = 32
HKDF_SALT_BYTES = 16

KDF_ALGORITHM = "HKDF-SHA256"
KEY_WRAP_ALGORITHM = "AES-256-KW"


class PortableKeyEnvelopeOwner:
    """
    Canonical owner of portable project-key recovery
    envelopes.

    The recovery root key is never persisted inside a
    project envelope.

    This owner does not persist engineering data and does
    not perform project-payload encryption.
    """

    def generate_recovery_key(
        self,
    ) -> str:

        encoded = (
            base64.urlsafe_b64encode(
                secrets.token_bytes(
                    RECOVERY_KEY_BYTES
                )
            )
            .decode(
                "ascii"
            )
            .rstrip(
                "="
            )
        )

        return (
            RECOVERY_KEY_PREFIX
            +
            encoded
        )


    def recovery_key_fingerprint(
        self,
        recovery_key: str,
    ) -> str:

        raw = (
            self._decode_recovery_key(
                recovery_key
            )
        )

        return hashlib.sha256(
            b"LEAF|RECOVERY-KEY-FINGERPRINT|S1H|"
            +
            raw
        ).hexdigest()


    def wrap_project_key(
        self,
        *,
        project_id: str,
        owner_principal_id: str,
        project_key: bytes,
        recovery_key: str,
    ) -> dict[str, Any]:

        project_id = (
            self._validate_project_id(
                project_id
            )
        )

        owner_principal_id = (
            self._validate_principal_id(
                owner_principal_id
            )
        )

        project_key = bytes(
            project_key
        )

        if (
            len(
                project_key
            )
            !=
            PROJECT_KEY_BYTES
        ):
            raise ValueError(
                "project_key_length_invalid"
            )

        recovery_root = (
            self._decode_recovery_key(
                recovery_key
            )
        )

        salt = secrets.token_bytes(
            HKDF_SALT_BYTES
        )

        kek = self._derive_kek(
            recovery_root=
                recovery_root,

            salt=
                salt,

            project_id=
                project_id,

            owner_principal_id=
                owner_principal_id,
        )

        wrapped = aes_key_wrap(
            kek,
            project_key,
        )

        return {
            "schema":
                SCHEMA,

            "project_id":
                project_id,

            "owner_principal_id":
                owner_principal_id,

            "kdf_algorithm":
                KDF_ALGORITHM,

            "key_wrap_algorithm":
                KEY_WRAP_ALGORITHM,

            "project_key_bytes":
                PROJECT_KEY_BYTES,

            "recovery_key_fingerprint":
                self.recovery_key_fingerprint(
                    recovery_key
                ),

            "kdf_salt":
                self._encode(
                    salt
                ),

            "wrapped_project_key":
                self._encode(
                    wrapped
                ),
        }


    def unwrap_project_key(
        self,
        *,
        envelope: dict[str, Any],
        recovery_key: str,
        expected_project_id: str,
        expected_owner_principal_id: str,
    ) -> bytes:

        envelope = dict(
            envelope
        )

        expected_project_id = (
            self._validate_project_id(
                expected_project_id
            )
        )

        expected_owner_principal_id = (
            self._validate_principal_id(
                expected_owner_principal_id
            )
        )

        if (
            envelope.get(
                "schema"
            )
            !=
            SCHEMA
        ):
            raise ValueError(
                "portable_key_envelope_schema_invalid"
            )

        if (
            envelope.get(
                "kdf_algorithm"
            )
            !=
            KDF_ALGORITHM
        ):
            raise ValueError(
                "portable_key_envelope_kdf_invalid"
            )

        if (
            envelope.get(
                "key_wrap_algorithm"
            )
            !=
            KEY_WRAP_ALGORITHM
        ):
            raise ValueError(
                "portable_key_envelope_wrap_algorithm_invalid"
            )

        if (
            envelope.get(
                "project_key_bytes"
            )
            !=
            PROJECT_KEY_BYTES
        ):
            raise ValueError(
                "portable_key_envelope_key_size_invalid"
            )

        if (
            envelope.get(
                "project_id"
            )
            !=
            expected_project_id
        ):
            raise PermissionError(
                "portable_key_envelope_project_mismatch"
            )

        if (
            envelope.get(
                "owner_principal_id"
            )
            !=
            expected_owner_principal_id
        ):
            raise PermissionError(
                "portable_key_envelope_principal_mismatch"
            )

        expected_fingerprint = (
            self.recovery_key_fingerprint(
                recovery_key
            )
        )

        stored_fingerprint = str(
            envelope.get(
                "recovery_key_fingerprint",
                "",
            )
        )

        if not hmac.compare_digest(
            expected_fingerprint,
            stored_fingerprint,
        ):
            raise PermissionError(
                "portable_recovery_key_mismatch"
            )

        recovery_root = (
            self._decode_recovery_key(
                recovery_key
            )
        )

        salt = self._decode(
            envelope.get(
                "kdf_salt",
                "",
            )
        )

        if (
            len(
                salt
            )
            !=
            HKDF_SALT_BYTES
        ):
            raise ValueError(
                "portable_key_envelope_salt_invalid"
            )

        wrapped = self._decode(
            envelope.get(
                "wrapped_project_key",
                "",
            )
        )

        kek = self._derive_kek(
            recovery_root=
                recovery_root,

            salt=
                salt,

            project_id=
                expected_project_id,

            owner_principal_id=
                expected_owner_principal_id,
        )

        try:

            project_key = (
                aes_key_unwrap(
                    kek,
                    wrapped,
                )
            )

        except InvalidUnwrap as exc:

            raise PermissionError(
                "portable_project_key_recovery_failed"
            ) from exc

        if (
            len(
                project_key
            )
            !=
            PROJECT_KEY_BYTES
        ):
            raise RuntimeError(
                "recovered_project_key_length_invalid"
            )

        return project_key


    @staticmethod
    def _derive_kek(
        *,
        recovery_root: bytes,
        salt: bytes,
        project_id: str,
        owner_principal_id: str,
    ) -> bytes:

        info = (
            "LEAF|PROJECT-RECOVERY-KEK|S1H|"
            f"{project_id}|"
            f"{owner_principal_id}"
        ).encode(
            "utf-8"
        )

        return HKDF(
            algorithm=
                hashes.SHA256(),

            length=
                32,

            salt=
                salt,

            info=
                info,
        ).derive(
            recovery_root
        )


    @staticmethod
    def _validate_project_id(
        project_id: str,
    ) -> str:

        project_id = str(
            project_id
            or ""
        ).strip()

        if not project_id.startswith(
            "project_"
        ):
            raise ValueError(
                "project_id_invalid"
            )

        return project_id


    @staticmethod
    def _validate_principal_id(
        principal_id: str,
    ) -> str:

        principal_id = str(
            principal_id
            or ""
        ).strip()

        if not principal_id.startswith(
            "principal_"
        ):
            raise ValueError(
                "principal_id_invalid"
            )

        return principal_id


    @staticmethod
    def _decode_recovery_key(
        recovery_key: str,
    ) -> bytes:

        recovery_key = str(
            recovery_key
            or ""
        ).strip()

        if not recovery_key.startswith(
            RECOVERY_KEY_PREFIX
        ):
            raise ValueError(
                "recovery_key_format_invalid"
            )

        encoded = recovery_key[
            len(
                RECOVERY_KEY_PREFIX
            ):
        ]

        raw = (
            PortableKeyEnvelopeOwner
            ._decode(
                encoded
            )
        )

        if (
            len(
                raw
            )
            !=
            RECOVERY_KEY_BYTES
        ):
            raise ValueError(
                "recovery_key_length_invalid"
            )

        return raw


    @staticmethod
    def _encode(
        payload: bytes,
    ) -> str:

        return (
            base64.urlsafe_b64encode(
                bytes(
                    payload
                )
            )
            .decode(
                "ascii"
            )
            .rstrip(
                "="
            )
        )


    @staticmethod
    def _decode(
        payload: str,
    ) -> bytes:

        payload = str(
            payload
            or ""
        )

        padding = (
            "="
            *
            (
                (
                    4
                    -
                    len(
                        payload
                    )
                    %
                    4
                )
                %
                4
            )
        )

        try:

            return (
                base64.urlsafe_b64decode(
                    (
                        payload
                        +
                        padding
                    )
                    .encode(
                        "ascii"
                    )
                )
            )

        except Exception as exc:

            raise ValueError(
                "portable_key_envelope_encoding_invalid"
            ) from exc
