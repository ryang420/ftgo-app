from dataclasses import dataclass, field


@dataclass(slots=True)
class CreateConsumerAddressCommand:
    label: str
    street1: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    street2: str | None = None


@dataclass(slots=True)
class CreateConsumerCommand:
    email: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    addresses: list[CreateConsumerAddressCommand] = field(default_factory=list)
