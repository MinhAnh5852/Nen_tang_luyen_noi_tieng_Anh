FROM nginx:alpine

# Xóa cấu hình mặc định
RUN rm -rf /usr/share/nginx/html/*

# Sao chép nội dung thư mục Learner vào thư mục gốc của Nginx
COPY ./Learner /usr/share/nginx/html

# Cấp quyền truy cập
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]