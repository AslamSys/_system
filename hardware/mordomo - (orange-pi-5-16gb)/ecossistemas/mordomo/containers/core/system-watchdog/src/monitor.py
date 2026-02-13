import psutil
import os

class SystemMonitor:
    def get_cpu_temp(self) -> float:
        """Lê a temperatura da CPU (Zona 0)."""
        try:
            # Tenta ler do arquivo de sistema padrão em Linux/Orange Pi
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_str = f.read().strip()
                return float(temp_str) / 1000.0
        except FileNotFoundError:
            # Fallback para psutil se disponível (nem sempre funciona em ARM)
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
            return 0.0
        except Exception as e:
            print(f"Erro ao ler temperatura: {e}")
            return 0.0

    def get_ram_usage(self) -> float:
        """Retorna a porcentagem de uso de RAM."""
        return psutil.virtual_memory().percent

    def get_cpu_usage(self) -> float:
        """Retorna a porcentagem de uso de CPU."""
        return psutil.cpu_percent(interval=0.1)

    def get_status(self) -> dict:
        return {
            "cpu_temp": self.get_cpu_temp(),
            "ram_usage": self.get_ram_usage(),
            "cpu_usage": self.get_cpu_usage()
        }
