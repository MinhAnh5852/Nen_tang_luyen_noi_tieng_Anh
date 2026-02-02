# Bước 1: Sử dụng Nginx để phục vụ nội dung tĩnh
FROM nginx:alpine

# Bước 2: Copy thư mục dist vừa build vào thư mục mặc định của Nginx
COPY dist /usr/share/nginx/html

# Bước 3: Copy file cấu hình nginx (nếu bạn có cấu hình riêng cho React Router)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]