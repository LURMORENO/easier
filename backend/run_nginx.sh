docker run -d \
  --name nginx-proxy \
  --network easier-network \
  -p 80:80 -p 443:443 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /opt/easier-certs-flat:/etc/ssl/easier:ro \
  nginx