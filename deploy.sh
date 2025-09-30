#!/bin/bash

# HPO Tree Visualizer Deployment Script
# Run this on your VPS (Ubuntu/Debian)

echo "🚀 Deploying HPO Tree Visualizer..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv nginx

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Create application directory
sudo mkdir -p /var/www/hpo-visualizer
sudo chown $USER:$USER /var/www/hpo-visualizer
cd /var/www/hpo-visualizer

# Copy your files here (or clone from git)
# git clone https://github.com/your-username/hpo-visualizer.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/hpo-visualizer.service > /dev/null <<EOF
[Unit]
Description=HPO Tree Visualizer
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/hpo-visualizer
Environment=PATH=/var/www/hpo-visualizer/venv/bin
ExecStart=/var/www/hpo-visualizer/venv/bin/uvicorn hpo_backend:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
sudo tee /etc/nginx/sites-available/hpo-visualizer > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        root /var/www/hpo-visualizer;
        index hpo_frontend.html;
        try_files \$uri \$uri/ /hpo_frontend.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/hpo-visualizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable hpo-visualizer
sudo systemctl start hpo-visualizer

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: http://your-domain.com"
echo "📊 Check status: sudo systemctl status hpo-visualizer"
echo "📝 View logs: sudo journalctl -u hpo-visualizer -f"
