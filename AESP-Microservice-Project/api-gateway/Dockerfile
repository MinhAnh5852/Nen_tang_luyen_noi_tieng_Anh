# Sử dụng Nginx phiên bản nhẹ
FROM nginx:alpine

# Xóa cấu hình mặc định để tránh xung đột cổng 80
RUN rm /etc/nginx/conf.d/default.conf

# Copy file cấu hình API Gateway của AESP vào đúng thư mục chính của Nginx
# Lưu ý: File nginx.conf của bạn chứa cả khối 'http {}', nên copy vào đường dẫn này là chính xác
COPY nginx.conf /etc/nginx/nginx.conf

# Mở cổng 80 để tiếp nhận các yêu cầu từ học viên (Learner) và Admin
EXPOSE 80

# Chạy Nginx ở chế độ foreground để Docker container không bị tự động tắt
CMD ["nginx", "-g", "daemon off;"]