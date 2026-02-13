# 💰 Wallet Integrator

**Container:** `wallet-integrator`  
**Stack:** Node.js + SDKs (PicPay, Mercado Pago, PayPal)  
**Propósito:** Integração com carteiras digitais

---

## 📋 Propósito

Integração com carteiras digitais para pagamentos e recebimentos. Suporte a PicPay, Mercado Pago, PayPal e PagSeguro.

---

## 🎯 Features

- ✅ PicPay (envio/recebimento)
- ✅ Mercado Pago (checkout, QR Code)
- ✅ PayPal (internacional)
- ✅ PagSeguro (boleto + cartão)

---

## 🔌 NATS Topics

### Subscribe
```javascript
Topic: "pagamentos.wallet.send"
Payload: {
  "wallet": "picpay",
  "recipient": "@joaosilva",
  "amount": 50.00
}
```

### Publish
```javascript
Topic: "pagamentos.wallet.sent"
Payload: {
  "wallet": "picpay",
  "txid": "PICPAY123456",
  "status": "success"
}
```

---

## 🚀 Docker Compose

```yaml
wallet-integrator:
  build: ./wallet-integrator
  environment:
    - PICPAY_TOKEN=${PICPAY_TOKEN}
    - MERCADOPAGO_TOKEN=${MERCADOPAGO_TOKEN}
    - PAYPAL_CLIENT_ID=${PAYPAL_CLIENT_ID}
  deploy:
    resources:
      limits:
        cpus: '0.35'
        memory: 256M
```

---

## 🧪 Código

```javascript
const axios = require('axios');

async function sendPicPay(recipient, amount) {
    const response = await axios.post('https://appws.picpay.com/ecommerce/public/payments', {
        referenceId: `MORDOMO_${Date.now()}`,
        callbackUrl: 'https://mordomo/webhooks/picpay',
        returnUrl: 'https://mordomo/payment/success',
        value: amount,
        buyer: {
            firstName: 'Mordomo',
            email: 'mordomo@exemplo.com'
        }
    }, {
        headers: { 'x-picpay-token': process.env.PICPAY_TOKEN }
    });
    
    return response.data.paymentUrl;
}
```

---

## 🔄 Changelog

### v1.0.0
- ✅ PicPay integration
- ✅ Mercado Pago support
- ✅ PayPal international
