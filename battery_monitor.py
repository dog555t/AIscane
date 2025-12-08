import logging
import os
import subprocess
import time
from pathlib import Path

from smbus2 import SMBus

LOG_PATH = Path("data/battery.log")
I2C_ADDRESS = 0x36  # MAX17043/44 fuel gauge default address
LOW_BATTERY_THRESHOLD = 10  # percent
CHECK_INTERVAL = 60  # seconds


class FuelGauge:
    def __init__(self, bus: int = 1, address: int = I2C_ADDRESS):
        self.bus_num = bus
        self.address = address

    def read_percentage(self) -> float:
        with SMBus(self.bus_num) as bus:
            msb = bus.read_byte_data(self.address, 0x04)
            lsb = bus.read_byte_data(self.address, 0x05)
            raw = (msb << 8) | lsb
            percentage = raw / 256.0
            return round(percentage, 2)

    def read_voltage(self) -> float:
        with SMBus(self.bus_num) as bus:
            msb = bus.read_byte_data(self.address, 0x02)
            lsb = bus.read_byte_data(self.address, 0x03)
            raw = (msb << 8) | lsb
            voltage = (raw >> 4) * 1.25 / 1000  # volts
            return round(voltage, 3)


def ensure_log_dir() -> None:
    os.makedirs(LOG_PATH.parent, exist_ok=True)


def configure_logging() -> None:
    ensure_log_dir()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(),
        ],
    )


def shutdown_system() -> None:
    logging.warning("Battery below threshold. Initiating safe shutdown...")
    try:
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
    except subprocess.CalledProcessError as exc:
        logging.error("Failed to shutdown: %s", exc)


def monitor_loop():
    configure_logging()
    gauge = FuelGauge()
    while True:
        try:
            percent = gauge.read_percentage()
            voltage = gauge.read_voltage()
            logging.info("Battery: %.2f%% | %.3f V", percent, voltage)
            if percent <= LOW_BATTERY_THRESHOLD:
                shutdown_system()
                break
        except OSError as exc:
            logging.error("I2C read failed: %s", exc)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor_loop()
