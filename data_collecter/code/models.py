import dataclasses

@dataclasses.dataclass
class DeviceData:
    name: str
    ip_address: str
    port: int
    username: str
    password: str
    os: str

@dataclasses.dataclass
class ReplyData:
    device_name: str
    reply: dict


@dataclasses.dataclass
class TelegrafFormat:
    measurement: str
    tags: dict[str, str]
    fields: dict[str, str]