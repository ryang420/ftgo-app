"""Application service helpers for consumer workflows."""

from app.application.commands import CreateConsumerAddressCommand, CreateConsumerCommand
from app.domain.models import ConsumerAddress, ConsumerProfile
from app.domain.repositories import ConsumerRepository


class ConsumerApplicationService:
    def __init__(self, consumer_repository: ConsumerRepository):
        self.consumer_repository = consumer_repository

    def list_consumers(self) -> list[ConsumerProfile]:
        return self.consumer_repository.list_consumers()

    def get_consumer(self, consumer_id: str) -> ConsumerProfile | None:
        return self.consumer_repository.get_consumer(consumer_id)

    def create_consumer(self, command: CreateConsumerCommand) -> ConsumerProfile:
        consumer = ConsumerProfile(
            email=command.email,
            first_name=command.first_name,
            last_name=command.last_name,
            phone_number=command.phone_number,
            addresses=[
                ConsumerAddress(
                    label=address.label,
                    street1=address.street1,
                    street2=address.street2,
                    city=address.city,
                    state=address.state,
                    postal_code=address.postal_code,
                    country=address.country,
                )
                for address in command.addresses
            ],
        )
        return self.consumer_repository.add(consumer)
