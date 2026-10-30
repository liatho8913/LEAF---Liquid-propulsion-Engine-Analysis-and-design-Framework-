from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from leaf_qt.key_envelope import (
    SCHEMA as PORTABLE_KEY_ENVELOPE_SCHEMA,
)
from leaf_qt.security_context import (
    VALID_SECURITY_CLASSIFICATIONS,
)


SCHEMA = "LEAF_AUTHENTICATED_CONTAINER_S1I_V1"

ENCRYPTION_ALGORITHM = "AES-256-GCM"

PROJECT_KEY_BYTES = 32
NONCE_BYTES = 12
AUTHENTICATION_TAG_BYTES = 16

PROJECT_ROOT_RESOURCE = "PROJECT_ROOT"
DESIGN_MANIFEST_RESOURCE = "DESIGN_MANIFEST"
ENGINEERING_STATE_RESOURCE = "ENGINEERING_STATE"
INTERNAL_REPORT_RESOURCE = "INTERNAL_REPORT"
VALIDATION_EVIDENCE_RESOURCE = "VALIDATION_EVIDENCE"
ENGINEERING_CACHE_RESOURCE = "ENGINEERING_CACHE"

INTERNAL_PROJECT_RESOURCE_TYPES = frozenset(
    {
        INTERNAL_REPORT_RESOURCE,
        VALIDATION_EVIDENCE_RESOURCE,
        ENGINEERING_CACHE_RESOURCE,
    }
)

ENCRYPTED_RESOURCE_TYPES = frozenset(
    {
        PROJECT_ROOT_RESOURCE,
        DESIGN_MANIFEST_RESOURCE,
        ENGINEERING_STATE_RESOURCE,
        INTERNAL_REPORT_RESOURCE,
        VALIDATION_EVIDENCE_RESOURCE,
        ENGINEERING_CACHE_RESOURCE,
    }
)


class EncryptedContainerOwner:
    """
    Canonical cryptographic transformation owner for
    protected LEAF project resources.

    It transforms structured payloads to and from
    authenticated ciphertext.

    It does not own filesystem persistence, OS key custody,
    user identity, GUI behaviour or engineering physics.
    """

    def seal(
        self,
        *,
        payload: dict[str, Any],
        project_id: str,
        owner_principal_id: str,
        security_classification: str,
        resource_type: str,
        resource_id: str,
        project_key: bytes,
        portable_key_envelope: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        project_id = self._validate_project_id(
            project_id
        )

        owner_principal_id = (
            self._validate_principal_id(
                owner_principal_id
            )
        )

        security_classification = (
            self._validate_classification(
                security_classification
            )
        )

        resource_type = (
            self._validate_resource_value(
                resource_type,
                "resource_type",
            )
        )

        resource_id = (
            self._validate_resource_value(
                resource_id,
                "resource_id",
            )
        )

        project_key = (
            self._validate_project_key(
                project_key
            )
        )

        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError(
                "encrypted_payload_must_be_dict"
            )

        portable_key_envelope = (
            self._validate_portable_envelope(
                portable_key_envelope,
                project_id=
                    project_id,
                owner_principal_id=
                    owner_principal_id,
                required=(
                    resource_type
                    ==
                    PROJECT_ROOT_RESOURCE
                ),
            )
        )

        envelope_fingerprint = (
            self._portable_envelope_fingerprint(
                portable_key_envelope
            )
        )

        metadata = self._metadata(
            project_id=
                project_id,
            owner_principal_id=
                owner_principal_id,
            security_classification=
                security_classification,
            resource_type=
                resource_type,
            resource_id=
                resource_id,
            portable_key_envelope_fingerprint=
                envelope_fingerprint,
        )

        plaintext = self._canonical_json(
            payload
        )

        aad = self._canonical_json(
            metadata
        )

        nonce = secrets.token_bytes(
            NONCE_BYTES
        )

        ciphertext = AESGCM(
            project_key
        ).encrypt(
            nonce,
            plaintext,
            aad,
        )

        return {
            **metadata,

            "nonce":
                self._encode(
                    nonce
                ),

            "ciphertext":
                self._encode(
                    ciphertext
                ),

            "portable_key_envelope":
                portable_key_envelope,
        }


    def open(
        self,
        *,
        container: dict[str, Any],
        project_key: bytes,
        expected_project_id: str,
        expected_owner_principal_id: str,
        expected_security_classification: str,
        expected_resource_type: str,
        expected_resource_id: str,
    ) -> dict[str, Any]:

        if not isinstance(
            container,
            dict,
        ):
            raise TypeError(
                "encrypted_container_must_be_dict"
            )

        project_key = (
            self._validate_project_key(
                project_key
            )
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

        expected_security_classification = (
            self._validate_classification(
                expected_security_classification
            )
        )

        expected_resource_type = (
            self._validate_resource_value(
                expected_resource_type,
                "expected_resource_type",
            )
        )

        expected_resource_id = (
            self._validate_resource_value(
                expected_resource_id,
                "expected_resource_id",
            )
        )

        if (
            container.get("schema")
            !=
            SCHEMA
        ):
            raise ValueError(
                "encrypted_container_schema_invalid"
            )

        if (
            container.get(
                "encryption_algorithm"
            )
            !=
            ENCRYPTION_ALGORITHM
        ):
            raise ValueError(
                "encrypted_container_algorithm_invalid"
            )

        if (
            container.get("project_id")
            !=
            expected_project_id
        ):
            raise PermissionError(
                "encrypted_container_project_mismatch"
            )

        if (
            container.get(
                "owner_principal_id"
            )
            !=
            expected_owner_principal_id
        ):
            raise PermissionError(
                "encrypted_container_principal_mismatch"
            )

        if (
            container.get(
                "security_classification"
            )
            !=
            expected_security_classification
        ):
            raise PermissionError(
                "encrypted_container_classification_mismatch"
            )

        if (
            container.get(
                "resource_type"
            )
            !=
            expected_resource_type
        ):
            raise PermissionError(
                "encrypted_container_resource_type_mismatch"
            )

        if (
            container.get(
                "resource_id"
            )
            !=
            expected_resource_id
        ):
            raise PermissionError(
                "encrypted_container_resource_id_mismatch"
            )

        portable_key_envelope = (
            self._validate_portable_envelope(
                container.get(
                    "portable_key_envelope"
                ),
                project_id=
                    expected_project_id,
                owner_principal_id=
                    expected_owner_principal_id,
                required=(
                    expected_resource_type
                    ==
                    PROJECT_ROOT_RESOURCE
                ),
            )
        )

        actual_fingerprint = (
            self._portable_envelope_fingerprint(
                portable_key_envelope
            )
        )

        stored_fingerprint = str(
            container.get(
                "portable_key_envelope_fingerprint",
                "",
            )
        )

        if not hmac.compare_digest(
            actual_fingerprint,
            stored_fingerprint,
        ):
            raise PermissionError(
                "encrypted_container_key_envelope_fingerprint_mismatch"
            )

        metadata = self._metadata(
            project_id=
                expected_project_id,
            owner_principal_id=
                expected_owner_principal_id,
            security_classification=
                expected_security_classification,
            resource_type=
                expected_resource_type,
            resource_id=
                expected_resource_id,
            portable_key_envelope_fingerprint=
                stored_fingerprint,
        )

        nonce = self._decode(
            container.get(
                "nonce",
                "",
            )
        )

        if len(nonce) != NONCE_BYTES:
            raise ValueError(
                "encrypted_container_nonce_invalid"
            )

        ciphertext = self._decode(
            container.get(
                "ciphertext",
                "",
            )
        )

        if (
            len(ciphertext)
            <
            AUTHENTICATION_TAG_BYTES
        ):
            raise ValueError(
                "encrypted_container_ciphertext_invalid"
            )

        try:
            plaintext = AESGCM(
                project_key
            ).decrypt(
                nonce,
                ciphertext,
                self._canonical_json(
                    metadata
                ),
            )

        except InvalidTag as exc:
            raise PermissionError(
                "encrypted_container_authentication_failed"
            ) from exc

        try:
            payload = json.loads(
                plaintext.decode(
                    "utf-8"
                )
            )
        except Exception as exc:
            raise ValueError(
                "encrypted_container_payload_invalid"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "encrypted_container_payload_not_object"
            )

        return payload


    @staticmethod
    def _metadata(
        *,
        project_id: str,
        owner_principal_id: str,
        security_classification: str,
        resource_type: str,
        resource_id: str,
        portable_key_envelope_fingerprint: str,
    ) -> dict[str, str]:

        return {
            "schema":
                SCHEMA,

            "project_id":
                project_id,

            "owner_principal_id":
                owner_principal_id,

            "security_classification":
                security_classification,

            "encryption_algorithm":
                ENCRYPTION_ALGORITHM,

            "resource_type":
                resource_type,

            "resource_id":
                resource_id,

            "portable_key_envelope_fingerprint":
                portable_key_envelope_fingerprint,
        }


    @staticmethod
    def _validate_portable_envelope(
        envelope: dict[str, Any] | None,
        *,
        project_id: str,
        owner_principal_id: str,
        required: bool,
    ) -> dict[str, Any] | None:

        if envelope is None:

            if required:
                raise ValueError(
                    "portable_key_envelope_required_for_project_root"
                )

            return None

        if not isinstance(
            envelope,
            dict,
        ):
            raise TypeError(
                "portable_key_envelope_must_be_dict"
            )

        envelope = dict(
            envelope
        )

        if (
            envelope.get("schema")
            !=
            PORTABLE_KEY_ENVELOPE_SCHEMA
        ):
            raise ValueError(
                "portable_key_envelope_schema_invalid"
            )

        if (
            envelope.get("project_id")
            !=
            project_id
        ):
            raise PermissionError(
                "portable_key_envelope_project_mismatch"
            )

        if (
            envelope.get(
                "owner_principal_id"
            )
            !=
            owner_principal_id
        ):
            raise PermissionError(
                "portable_key_envelope_principal_mismatch"
            )

        return envelope


    @classmethod
    def _portable_envelope_fingerprint(
        cls,
        envelope: dict[str, Any] | None,
    ) -> str:

        if envelope is None:
            return ""

        return hashlib.sha256(
            b"LEAF|PORTABLE-KEY-ENVELOPE|S1I|"
            +
            cls._canonical_json(
                envelope
            )
        ).hexdigest()


    @staticmethod
    def _validate_project_key(
        key: bytes,
    ) -> bytes:

        try:
            key = bytes(
                key
            )
        except Exception as exc:
            raise TypeError(
                "project_key_must_be_bytes"
            ) from exc

        if (
            len(key)
            !=
            PROJECT_KEY_BYTES
        ):
            raise ValueError(
                "project_key_length_invalid"
            )

        return key


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
    def _validate_classification(
        classification: str,
    ) -> str:

        classification = str(
            classification
            or ""
        ).strip()

        if (
            classification
            not in
            VALID_SECURITY_CLASSIFICATIONS
        ):
            raise ValueError(
                "security_classification_invalid"
            )

        return classification


    @staticmethod
    def _validate_resource_value(
        value: str,
        label: str,
    ) -> str:

        value = str(
            value
            or ""
        ).strip()


        if not value:
            raise ValueError(
                f"{label}_invalid"
            )


        if (
            label
            in {
                "resource_type",
                "expected_resource_type",
            }
            and
            value
            not in
            ENCRYPTED_RESOURCE_TYPES
        ):
            raise ValueError(
                "encrypted_resource_type_not_registered:"
                f"{value}"
            )


        return value


    @staticmethod
    def _canonical_json(
        value: Any,
    ) -> bytes:

        return json.dumps(
            value,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )


    @staticmethod
    def _encode(
        value: bytes,
    ) -> str:

        return (
            base64.urlsafe_b64encode(
                bytes(
                    value
                )
            )
            .decode(
                "ascii"
            )
        )


    @staticmethod
    def _decode(
        value: str,
    ) -> bytes:

        try:
            return (
                base64.urlsafe_b64decode(
                    str(
                        value
                        or ""
                    )
                    .encode(
                        "ascii"
                    )
                )
            )

        except Exception as exc:
            raise ValueError(
                "encrypted_container_encoding_invalid"
            ) from exc
