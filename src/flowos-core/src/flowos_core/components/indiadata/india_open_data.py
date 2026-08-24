import httpx

from flowos_core.custom.custom_component.component import Component
from flowos_core.inputs.inputs import IntInput, MessageTextInput, SecretStrInput, StrInput
from flowos_core.schema.data import Data
from flowos_core.schema.dataframe import DataFrame
from flowos_core.template.field.base import Output
from flowos_core.utils.ssrf_httpx import ssrf_safe_httpx_get
from flowos_core.utils.ssrf_protection import SSRFProtectionError

DATA_GOV_IN_BASE = "https://api.data.gov.in/resource"

# data.gov.in caps page size; asking for more is silently truncated, so bound
# it here rather than letting a user set a limit the API will ignore.
MAX_RECORDS = 100


class IndiaOpenDataComponent(Component):
    """Query a dataset on data.gov.in, India's national open-data portal."""

    display_name = "India Open Data"
    description = "Fetch records from data.gov.in (India's national open government data portal)."
    icon = "Landmark"
    documentation = "https://data.gov.in/apis"

    inputs = [
        StrInput(
            name="resource_id",
            display_name="Resource ID",
            info=(
                "The dataset's resource ID, taken from its data.gov.in API page "
                "(e.g. 9ef84268-d588-465a-a308-a864a43d0070)."
            ),
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="data.gov.in API Key",
            info="Register at https://data.gov.in to get a key.",
            required=True,
        ),
        MessageTextInput(
            name="search_query",
            display_name="Search",
            info=(
                "Optional full-text filter. Applied to the dataset's default "
                "searchable fields; leave blank to fetch the first N records."
            ),
            tool_mode=True,
        ),
        IntInput(
            name="limit",
            display_name="Max Records",
            info=f"Number of records to return (1-{MAX_RECORDS}).",
            value=10,
        ),
    ]

    outputs = [
        Output(display_name="Records", name="records", method="fetch_records"),
    ]

    def fetch_records(self) -> DataFrame:
        limit = max(1, min(int(self.limit or 10), MAX_RECORDS))

        params: dict[str, str | int] = {
            "api-key": self.api_key,
            "format": "json",
            "limit": limit,
        }
        # data.gov.in exposes full-text search as `q`; filters use the
        # `filters[field]` form, which we deliberately don't expose since the
        # field names differ per dataset.
        query = (self.search_query or "").strip()
        if query:
            params["q"] = query

        url = f"{DATA_GOV_IN_BASE}/{self.resource_id}"

        try:
            response = ssrf_safe_httpx_get(url, params=params, timeout=30)
            response.raise_for_status()
        except SSRFProtectionError as e:
            msg = f"SSRF protection blocked the request: {e}"
            raise ValueError(msg) from e
        except httpx.HTTPStatusError as e:
            msg = f"data.gov.in returned {e.response.status_code}: {e.response.text}"
            raise ValueError(msg) from e
        except httpx.HTTPError as e:
            msg = f"Could not reach data.gov.in: {e}"
            raise ValueError(msg) from e

        payload = response.json()
        records = payload.get("records", [])
        if not records:
            self.status = "No records found."
            return DataFrame([])

        self.status = f"Fetched {len(records)} record(s)."
        return DataFrame([Data(data=record) for record in records])
