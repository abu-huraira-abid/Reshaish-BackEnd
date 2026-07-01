from rest_framework import serializers

from properties.models import Property


class PropertySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_name = serializers.SerializerMethodField()
    owner_phone = serializers.CharField(source="owner.phone", read_only=True)
    images = serializers.SerializerMethodField()
    ownership_proof_url = serializers.SerializerMethodField()
    locked_for_editing = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "owner",
            "owner_email",
            "owner_name",
            "owner_phone",
            "title",
            "property_type",
            "address",
            "city",
            "bedrooms",
            "bathrooms",
            "area_sqft",
            "rent",
            "deposit",
            "facilities",
            "rules",
            "description",
            "status",
            "ownership_proof",
            "ownership_proof_url",
            "images",
            "locked_for_editing",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.email

    def get_ownership_proof_url(self, obj):
        if not obj.ownership_proof:
            return ""
        request = self.context.get("request")
        url = obj.ownership_proof.url
        return request.build_absolute_uri(url) if request else url

    def get_images(self, obj):
        request = self.context.get("request")
        images = []
        for image in obj.images.all():
            if not image.image:
                continue
            url = image.image.url
            images.append(
                {
                    "id": image.id,
                    "url": request.build_absolute_uri(url) if request else url,
                }
            )
        return images

    def get_locked_for_editing(self, obj):
        from agreements.models import Agreement

        return Agreement.objects.filter(
            property=obj,
            status__in=[
                Agreement.Status.PAYMENT_PENDING,
                Agreement.Status.ACTIVE,
                Agreement.Status.ENDED,
            ],
        ).exists()
