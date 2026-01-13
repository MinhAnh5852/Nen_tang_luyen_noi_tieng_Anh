# 1. Sử dụng Nginx Alpine siêu nhẹ
FROM nginx:alpine

# 2. Xóa sạch file mặc định của Nginx (Để không bao giờ hiện trang Welcome nữa)
RUN rm -rf /usr/share/nginx/html/*

# 3. Copy toàn bộ code (gồm index.html, folder admin, folder learner) vào container
COPY . /usr/share/nginx/html

# 4. Mở cổng
EXPOSE 80

# 5. Chạy Nginx
CMD ["nginx", "-g", "daemon off;"]
