from pymodbus.client import AsyncModbusSerialClient

class ModbusSensor:
    def __init__(self, port: str, baudrate: int, address: int, calibration_offset: float = 0):
        self.port = port
        self.baudrate = baudrate
        self.address = address
        self.calibration_offset = calibration_offset
        self.client = None

    async def connect(self):
        self.client = AsyncModbusSerialClient(
            method="rtu",
            port=self.port,
            baudrate=self.baudrate,
            stopbits=1,
            bytesize=8,
            parity='N',
            timeout=2
        )
        await self.client.connect()

    async def read_temperature(self) -> float:
        if not self.client or not self.client.connected:
            await self.connect()
        result = await self.client.read_input_registers(0, 1, unit=self.address)
        if result.isError():
            raise Exception("Modbus read error")
        value = result.registers[0] / 10.0 + self.calibration_offset
        return value

    async def close(self):
        if self.client:
            await self.client.close()
