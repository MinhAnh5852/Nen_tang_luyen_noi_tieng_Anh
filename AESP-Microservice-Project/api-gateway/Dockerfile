# 1. Sử dụng image Nginx nhẹ
FROM nginx:alpine

# 2. Xóa cấu hình mặc định của Nginx (để tránh xung đột)
RUN rm /etc/nginx/conf.d/default.conf

# 3. Copy file cấu hình của bạn vào container
COPY nginx.conf /etc/nginx/nginx.conf

# 4. Mở cổng 80
EXPOSE 80