from abc import ABC, abstractmethod
from typing import Any, Dict

class IODevice(ABC):
    """
    Port interface for I/O devices.
    """

    @property
    @abstractmethod
    def device_id(self) -> str:
        """
        Unique identifier for the I/O device.
        """
        pass

    @property
    @abstractmethod
    def device_type(self) -> str:
        """
        Type of the I/O device.
        """
        pass

    @abstractmethod
    async def read(self) -> Any:
        """
        Read data from the I/O device.
        """
        pass

    @abstractmethod
    async def write(self, data: Dict[str, Any]) -> None:
        """
        Write data to the I/O device.
        """
        pass

    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the I/O device.
        """
        try:
            current_value = await self.read()
            return {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "status": "online", # To-Do: Remove this magic value
                "data": current_value
            }
        except Exception as e:
            return {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "status": "error",
                "message": str(e)
            }
