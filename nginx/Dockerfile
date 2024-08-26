# Minimal NGINX image

# Use the official image as a parent image
FROM nginx:alpine

# Copy NGINX configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Run NGINX
CMD ["nginx", "-g", "daemon off;"]

