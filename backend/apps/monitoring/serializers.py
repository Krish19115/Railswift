import re

from rest_framework import serializers

from .crypto import PnrEncryptionUnavailable, encrypt_pnr, fingerprint_pnr
from .models import PnrTracker


class PnrTrackerSerializer(serializers.ModelSerializer):
    pnr = serializers.CharField(write_only=True, min_length=10, max_length=10, trim_whitespace=True)
    masked_pnr = serializers.SerializerMethodField()

    class Meta:
        model = PnrTracker
        fields = ("id", "pnr", "masked_pnr", "status", "last_checked_at", "created_at", "updated_at")
        read_only_fields = ("id", "masked_pnr", "status", "last_checked_at", "created_at", "updated_at")

    def validate_pnr(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise serializers.ValidationError("Enter a 10-digit PNR number.")
        return value

    def get_masked_pnr(self, obj):
        try:
            return obj.masked_pnr
        except PnrEncryptionUnavailable:
            return "••••••••••"

    def create(self, validated_data):
        pnr = validated_data.pop("pnr")
        try:
            validated_data["encrypted_pnr"] = encrypt_pnr(pnr)
            validated_data["pnr_fingerprint"] = fingerprint_pnr(pnr)
        except PnrEncryptionUnavailable as exc:
            raise serializers.ValidationError({"pnr": str(exc)}) from exc
        return super().create(validated_data)
