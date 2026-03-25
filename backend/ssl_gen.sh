cat > /home/jmartinpizarro/backend/setup_certs.sh << 'EOF'
#!/bin/bash

DOMAIN="easier-api.hulat.uc3m.es"
EMAIL="REPLACE@pa.uc3m.es"
CERTS_FLAT="/opt/easier-certs-flat"
CERTS_LE="/opt/easier-certs"

echo "=== [1/4] Parando nginx-proxy para liberar puerto 80 ==="
docker stop nginx-proxy 2>/dev/null && echo "nginx-proxy parado" || echo "nginx-proxy no estaba corriendo"

echo ""
echo "=== [2/4] Verificando que el puerto 80 está libre ==="
if sudo ss -tlnp | grep -q ':80'; then
    echo "ERROR: El puerto 80 sigue ocupado. Proceso:"
    sudo lsof -i :80
    exit 1
fi
echo "Puerto 80 libre. Continuando..."

echo ""
echo "=== [3/4] Generando certificados con certbot (Docker) ==="
sudo docker run --rm \
  -p 80:80 \
  -v ${CERTS_LE}:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  --non-interactive \
  --agree-tos \
  --email ${EMAIL} \
  -d ${DOMAIN}

if [ $? -ne 0 ]; then
    echo "ERROR: certbot falló. Revisa el output anterior."
    exit 1
fi
echo "Certificados generados correctamente."

echo ""
echo "=== [4/4] Copiando certificados sin symlinks a ${CERTS_FLAT} ==="
sudo mkdir -p ${CERTS_FLAT}

sudo cp -L ${CERTS_LE}/live/${DOMAIN}/fullchain.pem ${CERTS_FLAT}/fullchain.pem
sudo cp -L ${CERTS_LE}/live/${DOMAIN}/privkey.pem   ${CERTS_FLAT}/privkey.pem

if [ ! -s "${CERTS_FLAT}/fullchain.pem" ] || [ ! -s "${CERTS_FLAT}/privkey.pem" ]; then
    echo "ERROR: Los archivos no se copiaron correctamente."
    exit 1
fi

echo "Certificados copiados:"
ls -lh ${CERTS_FLAT}/
echo ""
head -1 ${CERTS_FLAT}/fullchain.pem

echo ""
echo "=== DONE: Ahora ejecuta ./run_nginx.sh ==="
EOF

chmod +x /home/jmartinpizarro/backend/setup_certs.sh
echo "Script creado. Ejecuta con: sudo ./setup_certs.sh"