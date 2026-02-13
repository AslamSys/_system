import docker
import os
import time

class WatchdogController:
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Erro ao conectar no Docker: {e}")
            self.docker_client = None

        # Lista de prioridade para sacrifício (do menos importante para o mais importante)
        self.sacrificial_lambs = [
            "dashboard-ui",
            "grafana",
            "prometheus",
            "source-separation",
            "whisper-asr" # Se tiver muito pesado
        ]
        
        self.current_defcon = 1

    def determine_defcon(self, temp: float, ram: float) -> int:
        """Calcula o nível DEFCON baseado em métricas."""
        if temp > 85 or ram > 98:
            return 4 # EMERGÊNCIA
        elif temp > 75 or ram > 90:
            return 3 # CRÍTICO
        elif temp > 65 or ram > 80:
            return 2 # ALERTA
        else:
            return 1 # NORMAL

    def execute_defense(self, defcon: int):
        """Executa ações baseadas no nível DEFCON."""
        if defcon == self.current_defcon:
            return # Nada mudou

        print(f"🚨 MUDANÇA DE DEFCON: {self.current_defcon} -> {defcon}")
        self.current_defcon = defcon

        if defcon == 1:
            self._set_fan_speed(30)
            # Opcional: Tentar reviver containers mortos se a situação normalizou?
            # Por segurança, melhor deixar manual ou implementar lógica de recovery lenta.

        elif defcon == 2:
            self._set_fan_speed(70)
            # Apenas alerta (já feito via NATS no main loop)

        elif defcon == 3:
            self._set_fan_speed(100)
            self._sacrifice_containers(level="soft")

        elif defcon == 4:
            self._set_fan_speed(100)
            self._sacrifice_containers(level="hard")
            if self._get_temp() > 90:
                print("🔥 TEMPERATURA CRÍTICA! INICIANDO SHUTDOWN...")
                os.system("shutdown now")

    def _set_fan_speed(self, speed_percent: int):
        """
        Controla ventoinha via PWM (Simulado/Genérico).
        No Orange Pi 5, isso geralmente é via /sys/class/pwm ou gpio.
        Aqui deixaremos um placeholder ou comando genérico.
        """
        print(f"💨 Ajustando ventoinha para {speed_percent}%")
        # Implementação real depende do driver específico do OPi5
        # Exemplo: echo 100 > /sys/class/thermal/cooling_device0/cur_state

    def _sacrifice_containers(self, level: str):
        if not self.docker_client:
            return

        print(f"⚔️ Executando sacrifício nível {level}...")
        
        targets = []
        if level == "soft":
            targets = self.sacrificial_lambs[:2] # Mata UI e Monitoramento
        elif level == "hard":
            targets = self.sacrificial_lambs # Mata tudo da lista

        for container_name in targets:
            try:
                container = self.docker_client.containers.get(container_name)
                if container.status == 'running':
                    print(f"💀 Matando {container_name} para economizar recursos...")
                    container.stop(timeout=5)
            except docker.errors.NotFound:
                pass
            except Exception as e:
                print(f"Erro ao parar {container_name}: {e}")

    def _get_temp(self):
        # Helper rápido para checar temp no shutdown
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return float(f.read().strip()) / 1000.0
        except:
            return 100.0 # Assume o pior se não conseguir ler
