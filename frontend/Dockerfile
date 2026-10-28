FROM nginx:alpine

# Salin hasil build Quasar Vite SPA
COPY dist/spa /usr/share/nginx/html

# Salin konfigurasi Nginx SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
