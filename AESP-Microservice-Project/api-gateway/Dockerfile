
# 1. Sử dụng Nginx Alpine nhẹ
FROM nginx:alpine

# 2. Xóa cấu hình mặc định của Nginx 
RUN rm /etc/nginx/conf.d/default.conf

# 3. Copy file nginx.conf của mình đè lên file cấu hình gốc của Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# 4. Mở cổng 80
EXPOSE 80

# 5. Chạy Nginx
CMD ["nginx", "-g", "daemon off;"]