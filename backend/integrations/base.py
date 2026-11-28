class ProviderUnavailable(Exception):
    """Raised when a permitted railway source is not configured or is offline."""


class RailwayDataProvider:
    """Adapter contract for explicitly authorized railway information services."""

    authorized = False
    source_label = "unconfigured"

    def get_pnr_status(self, pnr: str) -> dict:
        raise ProviderUnavailable("PNR status source is unavailable.")

    def get_chart(self, train_number: str, journey_date: str) -> dict:
        raise ProviderUnavailable("Reservation chart source is unavailable.")
