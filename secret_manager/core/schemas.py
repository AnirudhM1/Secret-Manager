from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class Backend(str, Enum):
    S3 = "s3"
    NONE = "none"


class SecretMode(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


@dataclass
class AWSConfig:
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    def serialize(self) -> dict[str]:
        return asdict(self)

    @classmethod
    def deserialize(cls, data: dict[str]):
        return cls(**data)


@dataclass
class Secret:
    path: Path
    backend: Backend
    aws_config: AWSConfig = None

    def serialize(self) -> dict[str]:
        return {
            "path": self.path.absolute().as_posix(),
            "backend": self.backend.value,
            "aws_config": self.aws_config.serialize() if self.aws_config else None,
        }

    @classmethod
    def deserialize(cls, data: dict[str]):
        path = Path(data["path"])
        backend = Backend(data["backend"])
        aws_config = AWSConfig.deserialize(data["aws_config"]) if data.get("aws_config") else None
        return cls(path=path, backend=backend, aws_config=aws_config)


@dataclass
class Project:
    root: Path
    local: Secret = None
    dev: Secret = None
    prod: Secret = None

    def serialize(self) -> dict[str]:
        return {
            "root": self.root.absolute().as_posix(),
            "local": self.local.serialize() if self.local else None,
            "dev": self.dev.serialize() if self.dev else None,
            "prod": self.prod.serialize() if self.prod else None,
        }

    @classmethod
    def deserialize(cls, data: dict[str]):
        root = Path(data["root"])
        local = Secret.deserialize(data["local"]) if data.get("local") else None
        dev = Secret.deserialize(data["dev"]) if data.get("dev") else None
        prod = Secret.deserialize(data["prod"]) if data.get("prod") else None

        return cls(root=root, local=local, dev=dev, prod=prod)
