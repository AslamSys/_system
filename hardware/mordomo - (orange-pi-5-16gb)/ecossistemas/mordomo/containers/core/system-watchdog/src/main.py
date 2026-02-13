import asyncio
import os
import json
import nats
from monitor import SystemMonitor
from controller import WatchdogController

async def main():
    # Configuração
    nats_url = os.getenv("NATS_URL", "nats://nats:4222")
    
    print(f"Iniciando System Watchdog...")
    print(f"Conectando ao NATS em {nats_url}...")

    # Inicializa componentes
    monitor = SystemMonitor()
    controller = WatchdogController()
    
    # Conexão NATS
    nc = await nats.connect(nats_url)
    print("Conectado ao NATS!")

    try:
        while True:
            # 1. Coleta Métricas
            status = monitor.get_status()
            temp = status['cpu_temp']
            ram = status['ram_usage']
            
            # 2. Determina e Executa Defesa
            defcon = controller.determine_defcon(temp, ram)
            controller.execute_defense(defcon)
            
            # 3. Adiciona info de DEFCON ao status
            status['defcon'] = defcon
            
            # 4. Publica Heartbeat
            await nc.publish("system.health.status", json.dumps(status).encode())
            
            # 5. Publica Alertas Específicos
            if defcon >= 2:
                await nc.publish("system.health.warning", json.dumps({
                    "level": "warning" if defcon == 2 else "critical",
                    "message": f"Sistema sob carga! Temp: {temp}°C, RAM: {ram}%",
                    "defcon": defcon
                }).encode())

            # Intervalo de polling (mais rápido se estiver quente)
            sleep_time = 10 if defcon == 1 else 5
            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Encerrando Watchdog...")
    finally:
        await nc.close()

if __name__ == "__main__":
    asyncio.run(main())
