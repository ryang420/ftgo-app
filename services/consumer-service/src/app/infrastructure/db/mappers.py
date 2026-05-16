from app.domain.models import ConsumerAddress, ConsumerProfile
from app.infrastructure.db.models import ConsumerAddressRecord, ConsumerProfileRecord


def to_domain_consumer(record: ConsumerProfileRecord) -> ConsumerProfile:
    return ConsumerProfile(
        id=record.id,
        email=record.email,
        first_name=record.first_name,
        last_name=record.last_name,
        phone_number=record.phone_number,
        created_at=record.created_at,
        updated_at=record.updated_at,
        addresses=[
            ConsumerAddress(
                id=address.id,
                label=address.label,
                street1=address.street1,
                street2=address.street2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country,
                created_at=address.created_at,
                updated_at=address.updated_at,
            )
            for address in record.addresses
        ],
    )


def to_consumer_record(consumer: ConsumerProfile) -> ConsumerProfileRecord:
    record = ConsumerProfileRecord(
        id=consumer.id,
        email=consumer.email,
        first_name=consumer.first_name,
        last_name=consumer.last_name,
        phone_number=consumer.phone_number,
    )
    record.addresses = [
        ConsumerAddressRecord(
            id=address.id,
            label=address.label,
            street1=address.street1,
            street2=address.street2,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country=address.country,
        )
        for address in consumer.addresses
    ]
    return record
