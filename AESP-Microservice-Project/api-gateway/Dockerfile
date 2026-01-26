FROM nginx:alpine

# Xóa cấu hình mặc định cũ
RUN rm -f /etc/nginx/conf.d/default.conf

# COPY VÀO ĐÚNG ĐƯỜNG DẪN NÀY
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]