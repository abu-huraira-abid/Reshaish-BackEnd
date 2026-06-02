from audit.models import AuditLog


def record_audit_log(
    *,
    action,
    entity_type,
    actor=None,
    entity_id="",
    metadata=None,
    ip_address=None,
):
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
        ip_address=ip_address,
    )
