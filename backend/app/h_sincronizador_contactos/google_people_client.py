"""Cliente HTTP para Google People API (contactos).

Gestiona el ciclo de vida del access_token (refresh automático) y
expone operaciones de alto nivel: crear contacto, actualizar contacto
y buscar por teléfono.

Upsert por teléfono: si el teléfono ya existe en los contactos → actualiza
displayName. Si no → crea el contacto. No usa grupos ni memberships.

Autenticación: OAuth 2.0 con refresh_token (Bearer token en cabecera).
"""

import logging
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)

_PEOPLE_API = "https://people.googleapis.com/v1"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_TIMEOUT = 20


class GooglePeopleClient:
    """Cliente para la API de Google Contacts (People API v1).

    El cliente recibe los tokens ya descifrados. El cifrado/descifrado
    de los tokens es responsabilidad del servicio que lo instancia.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str | None,
        refresh_token: str,
        token_expiry: datetime | None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expiry = token_expiry
        self._token_refreshed = False

    # ── Tokens ───────────────────────────────────────────────────────────

    def _ensure_valid_token(self) -> None:
        """Renueva el access_token si ha expirado o está ausente."""
        ahora = datetime.now(timezone.utc)
        expiry = self._token_expiry

        if (
            self._access_token is None
            or expiry is None
            or expiry <= ahora + timedelta(seconds=60)
        ):
            self._refresh_access_token()

    def _refresh_access_token(self) -> None:
        """Intercambia el refresh_token por un access_token nuevo."""
        resp = requests.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        self._token_refreshed = True
        logger.info("Google OAuth: access_token renovado")

    @property
    def token_refreshed(self) -> bool:
        return self._token_refreshed

    @property
    def current_access_token(self) -> str | None:
        return self._access_token

    @property
    def current_token_expiry(self) -> datetime | None:
        return self._token_expiry

    def _headers(self) -> dict:
        self._ensure_valid_token()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    # ── Contactos ────────────────────────────────────────────────────────

    def search_contact_by_phone(self, telefono: str) -> str | None:
        """Busca un contacto por teléfono. Devuelve resourceName o None."""
        resp = requests.get(
            f"{_PEOPLE_API}/people:searchContacts",
            headers=self._headers(),
            params={
                "query": telefono,
                "readMask": "phoneNumbers",
                "pageSize": 5,
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        normalized = telefono.replace(" ", "")
        for result in resp.json().get("results", []):
            person = result.get("person", {})
            for phone in person.get("phoneNumbers", []):
                if phone.get("value", "").replace(" ", "") == normalized:
                    return person.get("resourceName")
        return None

    def create_contact(self, payload: dict) -> str:
        """Crea un contacto nuevo. Devuelve su resourceName."""
        resp = requests.post(
            f"{_PEOPLE_API}/people:createContact",
            headers=self._headers(),
            json=payload,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["resourceName"]

    def update_contact(self, resource_name: str, payload: dict, update_mask: str) -> None:
        """Actualiza campos de un contacto existente."""
        resp = requests.get(
            f"{_PEOPLE_API}/{resource_name}",
            headers=self._headers(),
            params={"personFields": "names,phoneNumbers"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        etag = resp.json().get("etag", "")

        payload["etag"] = etag
        resp = requests.patch(
            f"{_PEOPLE_API}/{resource_name}:updateContact",
            headers=self._headers(),
            json=payload,
            params={"updatePersonFields": update_mask},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()

    def upsert_contact(self, payload: dict, telefono: str) -> tuple[str, bool]:
        """Crea o actualiza un contacto buscando por teléfono.

        Returns
        -------
        tuple[str, bool]
            (resourceName, es_nuevo).
        """
        resource_name = self.search_contact_by_phone(telefono)
        if resource_name:
            self.update_contact(resource_name, payload, "names,phoneNumbers")
            return resource_name, False

        resource_name = self.create_contact(payload)
        return resource_name, True
