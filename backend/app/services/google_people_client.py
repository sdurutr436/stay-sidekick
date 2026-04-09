"""Cliente HTTP para Google People API (contactos).

Gestiona el ciclo de vida del access_token (refresh automático) y
expone operaciones de alto nivel: crear contacto, actualizar contacto,
buscar por email y gestionar grupos de contactos.

Autenticación: OAuth 2.0 con refresh_token (Bearer token en cabecera).

Referencias:
- https://developers.google.com/people/api/rest
- Scopes necesarios: https://www.googleapis.com/auth/contacts
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
        self._token_refreshed = False  # indica si se renovó durante esta sesión

    # ── Tokens ───────────────────────────────────────────────────────────

    def _ensure_valid_token(self) -> None:
        """Renueva el access_token si ha expirado o está ausente."""
        ahora = datetime.now(timezone.utc)
        expiry = self._token_expiry

        # Renovar si el token falta, expiró o expirará en los próximos 60s
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
        self._token_expiry = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in
        )
        self._token_refreshed = True
        logger.info("Google OAuth: access_token renovado")

    @property
    def token_refreshed(self) -> bool:
        """True si el access_token fue renovado durante esta sesión."""
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

    # ── Grupos de contactos (etiquetas) ──────────────────────────────────

    def get_or_create_contact_group(self, nombre: str) -> str:
        """Devuelve el resourceName del grupo, creándolo si no existe.

        Parameters
        ----------
        nombre:
            Nombre del grupo (p.ej. nombre del apartamento).

        Returns
        -------
        str
            resourceName del grupo: "contactGroups/<id>".
        """
        existing = self._find_contact_group(nombre)
        if existing:
            return existing

        resp = requests.post(
            f"{_PEOPLE_API}/contactGroups",
            headers=self._headers(),
            json={"contactGroup": {"name": nombre}},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["resourceName"]

    def _find_contact_group(self, nombre: str) -> str | None:
        """Busca un grupo por nombre exacto. Devuelve resourceName o None."""
        resp = requests.get(
            f"{_PEOPLE_API}/contactGroups",
            headers=self._headers(),
            params={"pageSize": 200},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        for group in resp.json().get("contactGroups", []):
            if group.get("name") == nombre:
                return group["resourceName"]
        return None

    # ── Contactos ────────────────────────────────────────────────────────

    def search_contact_by_email(self, email: str) -> str | None:
        """Busca un contacto por email. Devuelve resourceName o None."""
        resp = requests.get(
            f"{_PEOPLE_API}/people:searchContacts",
            headers=self._headers(),
            params={
                "query": email,
                "readMask": "emailAddresses",
                "pageSize": 5,
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        for result in resp.json().get("results", []):
            person = result.get("person", {})
            for addr in person.get("emailAddresses", []):
                if addr.get("value", "").lower() == email.lower():
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
        # People API requiere el etag del contacto para hacer PATCH
        # Primero obtenemos el etag
        resp = requests.get(
            f"{_PEOPLE_API}/{resource_name}",
            headers=self._headers(),
            params={"personFields": "names,emailAddresses,phoneNumbers,biographies,memberships"},
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

    def upsert_contact(self, payload: dict, email: str | None) -> tuple[str, bool]:
        """Crea o actualiza un contacto según si ya existe el email.

        Returns
        -------
        tuple[str, bool]
            (resourceName, es_nuevo).
        """
        if email:
            resource_name = self.search_contact_by_email(email)
            if resource_name:
                update_mask = "names,emailAddresses,phoneNumbers,biographies,memberships"
                self.update_contact(resource_name, payload, update_mask)
                return resource_name, False

        resource_name = self.create_contact(payload)
        return resource_name, True
