# Ubuntu 22.04 后端部署文档



* 请根据实际情况修改数据库和域名配置，以及 Supervisor 配置中的路径、用户名等信息。

1. 更新系统和安装必要的软件包：

   ```bash
   sudo apt update
   sudo apt upgrade
   sudo apt install git python3 python3-pip python3-venv nginx supervisor
   ```

2. 添加 PostgreSQL 官方 APT 源并安装 PostgreSQL：

   ```bash
   # Create the file repository configuration:
   sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
   
   # Import the repository signing key:
   wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
   
   # Update the package lists:
   sudo apt-get update
   
   # Install the latest version of PostgreSQL.
   # If you want a specific version, use 'postgresql-12' or similar instead of 'postgresql':
   sudo apt-get -y install postgresql-13
   ```

3. 进入数据库命令行，准备创建数据库：

   ```bash
   sudo -u postgres psql
   ```

4. 创建数据库：

   ```SQL
   CREATE DATABASE mainbackend; -- 创建一个空数据库
   CREATE USER main WITH PASSWORD 'mypassword'; -- 创建一个用户
   GRANT ALL PRIVILEGES ON DATABASE mainbackend TO main; -- 授予数据库用户对数据库的所有权限
   \q
   ```

5. 获取源码并进入：

   ```bash
   git clone http://git.nmhuixin.com:3030/hxpackage/main-backend.git
   cd main-backend
   ```

6. 创建并激活虚拟环境：

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

7. 在虚拟环境中安装 Django 和 Gunicorn：

   ```bash
   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
   pip install -r requirements.txt
   ```

8. 复制配置文件：

   ```bash
   cp project/local_settings.py.example project/local_settings.py
   ```

9. 配置数据库连接： 编辑 project/local_settings.py 文件，找到 DATABASES 部分，修改为以下内容（根据创建数据库步骤的配置修改用户名、密码和数据库名）：

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django_postgrespool2',
           'NAME': 'mydatabase',
           'USER': 'myuser',
           'PASSWORD': 'mypassword',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   ```

10. 从备份数据恢复数据库（需要先把导出的数据库文件放到当前目录下）：

    ```bash
    python manage.py dbshell
    ```

    ```
    \i backup.sql
    \i parameter.sql
    ```

11. 测试 Django 项目是否正常运行：

    ```
    python manage.py runserver
    ```

12. 配置 Supervisor： 创建一个名为 `main.conf` 的 Supervisor 配置文件：

    ```
    sudo nano /etc/supervisor/conf.d/main.conf
    ```

    在文件中写入以下内容（根据实际情况修改项目路径和虚拟环境路径）：

    ```
    [program:main]
    command=/path/to/main-backend/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 project.wsgi
    directory=/path/to/main-backend
    user=当前用户名
    autostart=true
    autorestart=true
    redirect_stderr=true
    ```

13. 更新 Supervisor 配置并重新启动服务：

    ```
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart myproject
    ```

14. 配置 Nginx： 创建 Nginx 配置文件：

    ```
    sudo nano /etc/nginx/sites-available/main
    ```

    在文件中写入以下内容：

    ```
    server {
        listen 80;
        server_name 如果有域名请填写到此处，否则去掉本行;
    
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

15. 激活 Nginx 配置文件并重启 Nginx：

    ```
    sudo ln -s /etc/nginx/sites-available/main /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
    sudo systemctl restart nginx
    ```

16. 设置防火墙规则（如果有必要）：

    ```
    sudo ufw allow 'Nginx Full'
    ```

