from abc import ABC, abstractmethod
from typing import Any, Dict

class IODevice(ABC):
    """Abstract base class for I/O devices.

    Purpose:
            Provide a single, consistent contract for sensors, actuators, and
            hybrid devices. This simplifies orchestration and testing while
            keeping implementations interchangeable.

    Notes:
            - All I/O operations are asynchronous to support real network/IO and
                maintain a uniform public API across implementations.
            - Prefer raising domain-relevant exceptions in ``read``/``write`` and
                surfacing them via ``get_status`` to avoid breaking callers.

    Example:
            Basic device implementation:

            >>> class TemperatureSensor(IODevice):
            ...     def __init__(self):
            ...         self._id = "temp_01"
            ...         self._type = "temperature_sensor"
            ...         self._value = 23.5
            ...
            ...     @property
            ...     def device_id(self) -> str:
            ...         return self._id
            ...
            ...     @property
            ...     def device_type(self) -> str:
            ...         return self._type
            ...
            ...     async def read(self) -> float:
            ...         return self._value
            ...
            ...     async def write(self, data: Dict[str, Any]) -> None:
            ...         if "value" in data:
            ...             self._value = float(data["value"])
            ...
            >>> device = TemperatureSensor()
            >>> status = await device.get_status()
            >>> status["status"] in {"online", "error"}
            True
    """

    @property
    @abstractmethod
    def device_id(self) -> str:
        """Unique identifier for the I/O device.

        Returns:
            str: Stable, unique ID for registration and logging.

        Notes:
            Suggested convention: ``{type}_{sequence}`` (e.g., ``"temp_01"``,
            ``"valve_main"``). This value should be immutable for the lifetime
            of the device instance.
        """
        pass

    @property
    @abstractmethod
    def device_type(self) -> str:
        """Type/category of the I/O device.

        Returns:
            str: Device type label (e.g., ``"temperature_sensor"``, ``"motor"``,
            ``"valve"``).
        """
        pass

    @abstractmethod
    async def read(self) -> Any:
        """Read current data/state from the device.

        Returns:
            Any: Current device value. Typical patterns:
                - Sensors: measurement value (float/int/bool)
                - Actuators: current state/position
                - Hybrid: primary feedback value

        Raises:
            ConnectionError: Device unreachable or not responding.
            TimeoutError: Read operation exceeded time limit.
            ValueError: Invalid or unsupported payload returned by device.

        Notes:
            Implementations should keep this operation side-effect free.
        """
        pass

    @abstractmethod
    async def write(self, data: Dict[str, Any]) -> None:
        """Write data/command to the device.

        Args:
            data (Dict[str, Any]): Structured payload for the device. For
                simple devices, a common convention is ``{"value": <Any>}``.

        Raises:
            ConnectionError: Device unreachable or not responding.
            TimeoutError: Write operation exceeded time limit.
            ValueError: Invalid or unsupported payload for the device.

        Example:
            Set a new value on a simple device::

                await device.write({"value": 42})
        """
        pass

    async def get_status(self) -> Dict[str, Any]:
        """Get device status and diagnostics without raising exceptions.

        Performs a best-effort read and returns structured status data.

        Returns:
            Dict[str, Any]: Status payload with the following keys:
                - ``device_id`` (str): Device identifier
                - ``device_type`` (str): Device type string
                - ``status`` (str): "online" | "error"
                - ``data`` (Any): Present when status == "online"
                - ``message`` (str): Present when status == "error"

        Notes:
            - This method should not raise; errors are captured in the
              response for graceful degradation.
            - Adapters may extend the payload with extra diagnostic fields.
        """
        try:
            current_value = await self.read()
            return {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "status": "online",  # To-Do: Remove this magic value
                "data": current_value,
            }
        except Exception as e:
            return {
                "device_id": self.device_id,
                "device_type": self.device_type,
                "status": "error",
                "message": str(e),
            }
