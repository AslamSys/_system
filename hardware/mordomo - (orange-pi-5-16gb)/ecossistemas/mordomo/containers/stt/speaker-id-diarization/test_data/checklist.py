"""
Checklist de validação antes de rodar o serviço completo.
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║          SPEAKER ID/DIARIZATION - CHECKLIST DE VALIDAÇÃO        ║
╔══════════════════════════════════════════════════════════════════╗

📋 PRÉ-REQUISITOS

□ Python 3.10+ instalado
□ Microfone funcionando
□ Segunda pessoa disponível para testes

📦 INSTALAÇÃO

□ Dependências de teste instaladas:
  cd test_data
  pip install -r requirements.txt

🎤 CRIAÇÃO DE EMBEDDINGS

□ Embedding do usuário 1 criado:
  python create_embedding.py user_1

□ Embedding do usuário 2 criado:
  python create_embedding.py user_2

□ Arquivos verificados:
  ls embeddings/
  → user_1.npy ✓
  → user_2.npy ✓

🧪 TESTE DE DIARIZATION

□ Teste de separação executado:
  python test_diarization.py --duration 10

□ Resultados analisados:
  → Falantes detectados: ___
  → Taxa de reconhecimento: ____%
  → Trocas de falante: ___

□ Taxa de reconhecimento aceitável (>70%)?
  □ SIM → Prosseguir para Docker
  □ NÃO → Recriar embeddings com melhor qualidade

🐳 DOCKER (PRODUÇÃO)

□ Embeddings copiados para produção:
  mkdir -p ../data/embeddings
  cp embeddings/*.npy ../data/embeddings/

□ Variáveis de ambiente configuradas:
  cp .env.example .env
  # Editar .env conforme necessário

□ Container buildado:
  cd ..
  docker-compose build

□ Container rodando:
  docker-compose up -d

□ Logs verificados:
  docker-compose logs -f speaker-id-diarization

□ Health check OK:
  docker-compose ps
  → speaker-id-diarization (healthy) ✓

🔌 INTEGRAÇÃO

□ NATS disponível em nats://nats:4222
□ Whisper ASR pode conectar em :50053
□ Prometheus pode scrape em :8003

✅ VALIDAÇÃO FINAL

□ Serviço responde a gRPC requests
□ Publica resultados no NATS
□ Métricas disponíveis no Prometheus
□ Gate mechanism funcionando (buffering)
□ Hot reload de embeddings ativo

╚══════════════════════════════════════════════════════════════════╝

📚 DOCUMENTAÇÃO DISPONÍVEL:

   README.md      → Documentação completa do serviço
   STRUCTURE.md   → Estrutura do projeto
   QUICKSTART.md  → Guia rápido de teste
   test_data/README.md → Documentação dos scripts de teste

🚀 PRÓXIMO PASSO:

   Siga o QUICKSTART.md para criar embeddings e testar!

╚══════════════════════════════════════════════════════════════════╝
""")
