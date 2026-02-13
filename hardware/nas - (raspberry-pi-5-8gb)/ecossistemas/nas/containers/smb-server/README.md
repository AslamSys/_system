# 📁 SMB/Samba Server

**Container:** `smb-server`  
**Stack:** Samba  
**Propósito:** Compartilhamento de arquivos Windows/macOS

---

## 📋 Propósito

Shares SMB/CIFS para acesso de rede. Windows Explorer, macOS Finder, Linux mount.

---

## 🎯 Features

- ✅ SMB 3.0 (criptografado)
- ✅ Multi-user access control
- ✅ Guest access (opcional)
- ✅ Time Machine support (macOS backup)
- ✅ Recycle bin (arquivos deletados preservados)

---

## 🚀 Docker Compose

```yaml
smb-server:
  image: dperson/samba:latest
  ports:
    - "139:139"
    - "445:445"
  environment:
    - USERID=1000
    - GROUPID=1000
    - SHARE=photos;/photos;yes;no;no;renan
    - SHARE2=documents;/documents;yes;no;no;renan
    - USER=renan;${SMB_PASSWORD}
  volumes:
    - /hot-storage/photos:/photos
    - /hot-storage/documents:/documents
  deploy:
    resources:
      limits:
        cpus: '0.3'
        memory: 384M
```

---

## 🖥️ Cliente Windows

```powershell
# Map network drive
net use Z: \\nas.local\photos /user:renan password

# Ou via GUI
# Windows Explorer → This PC → Map Network Drive
# \\nas.local\photos
```

---

## 🍎 Cliente macOS

```bash
# Finder → Go → Connect to Server
# smb://nas.local/photos

# Time Machine backup
# System Preferences → Time Machine → Select Disk
# \\nas.local\timemachine
```

---

## 🔄 Changelog

### v1.0.0
- ✅ Samba 4.x
- ✅ SMB 3.0 encrypted
- ✅ Multi-user ACLs
- ✅ Time Machine support
