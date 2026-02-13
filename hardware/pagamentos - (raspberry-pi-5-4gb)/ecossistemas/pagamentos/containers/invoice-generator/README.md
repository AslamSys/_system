# 📄 Invoice Generator

**Container:** `invoice-generator`  
**Stack:** Node.js + Boleto.js + NFe.io  
**Propósito:** Gerar boletos e notas fiscais

---

## 📋 Propósito

Geração de boletos bancários, NFe (Nota Fiscal Eletrônica) e NFSe (Serviços). Integração com prefeituras e SEFAZ.

---

## 🎯 Features

- ✅ Boletos bancários (Banco do Brasil, Itaú, etc)
- ✅ NFe (SEFAZ)
- ✅ NFSe (prefeituras via NFe.io)
- ✅ Envio por email automático

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "pagamentos.invoice.generate"
Payload: {
  "type": "boleto|nfe|nfse",
  "amount": 500.00,
  "due_date": "2025-12-15",
  "recipient": {
    "name": "João Silva",
    "cpf": "123.456.789-00"
  }
}
```

### Publish
```javascript
Topic: "pagamentos.invoice.generated"
Payload: {
  "type": "boleto",
  "barcode": "34191.79001 01043.510047 91020.150008 1 96610000050000",
  "pdf_url": "https://storage/boleto_123.pdf"
}
```

---

## 🚀 Docker Compose

```yaml
invoice-generator:
  build: ./invoice-generator
  environment:
    - BANCO_BB_CONVENIO=${BB_CONVENIO}
    - NFE_IO_API_KEY=${NFE_IO_API_KEY}
    - STORAGE_URL=https://mordomo-minio:9000
  volumes:
    - ./invoices:/invoices
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 192M
```

---

## 🧪 Código

```javascript
const Boleto = require('node-boleto');

async function generateBoleto(data) {
    const boleto = new Boleto({
        banco: 'banco-do-brasil',
        data_emissao: new Date(),
        data_vencimento: new Date(data.due_date),
        valor: data.amount,
        nosso_numero: '00000001',
        numero_documento: '00001',
        cedente: 'Mordomo Automação',
        cedente_cnpj: '12.345.678/0001-00',
        agencia: '1234',
        codigo_cedente: '567890',
        carteira: '18',
        pagador: data.recipient.name,
        pagador_cpf: data.recipient.cpf
    });
    
    const pdf = await boleto.renderPDF();
    const path = `/invoices/boleto_${Date.now()}.pdf`;
    fs.writeFileSync(path, pdf);
    
    return {
        barcode: boleto.linha_digitavel,
        pdf_url: `https://storage${path}`
    };
}
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Boleto generation (BB)
- ✅ NFe.io integration
- ✅ PDF export
