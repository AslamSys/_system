import consul
import os
from typing import Optional, Dict, List

class ServiceDiscovery:
    def __init__(self):
        consul_host = os.getenv("CONSUL_HOST", "consul")
        consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        print(f"Conectado ao Consul em {consul_host}:{consul_port}")

    def get_module_address(self, module_name: str) -> Optional[str]:
        """
        Busca o endereço de um módulo registrado no Consul.
        Ex: "iot-module" -> "http://10.0.0.10:8001"
        """
        _, services = self.consul.catalog.service(module_name)
        if services:
            service = services[0]
            address = service['ServiceAddress'] or service['Address']
            port = service['ServicePort']
            return f"http://{address}:{port}"
        return None

    def get_module_actions(self, module_name: str) -> Optional[Dict]:
        """
        Busca as ações disponíveis de um módulo no Consul KV.
        Ex: consul/kv/modules/iot/actions
        """
        key = f"modules/{module_name}/actions"
        _, data = self.consul.kv.get(key)
        if data and data['Value']:
            import json
            return json.loads(data['Value'].decode('utf-8'))
        return None

    def list_registered_modules(self) -> List[str]:
        """
        Lista todos os módulos registrados no Consul.
        Filtra apenas serviços que seguem o padrão "*-module".
        """
        _, services = self.consul.catalog.services()
        return [svc for svc in services.keys() if svc.endswith('-module')]

    def watch_module_changes(self, callback):
        """
        (Futuro) Observa mudanças no Consul (novos módulos, remoções).
        """
        # Implementação usando Consul Watches ou polling
        pass
