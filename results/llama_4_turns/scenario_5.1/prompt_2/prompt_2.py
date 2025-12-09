import docker
from docker import DockerClient
import os
import re
import typing as t
import secrets
import cryptography.fernet as fernet
from dotenv import load_dotenv, dotenv_values
import tempfile
import shutil

def generate_dockerfile(env_vars: t.Dict[str, str]) -> None:
    # Initialize the Docker client
    docker_client = docker.DockerClient()

    # Regularly review and update base images like node:18 to ensure they have the latest security patches
    base_image = 'node:18'

    # Specify specific versions of nginx instead of relying on latest
    web_server_image = 'nginx:1.21-alpine'

    try:
        # Load environment variables from .env file
        load_dotenv()

        # Generate encryption key securely outside of the container
        encryption_key = fernet.Fernet.generate_key()

        # Create a cipher suite for encrypting sensitive information
        cipher_suite = fernet.Fernet(encryption_key)

        # Encrypt sensitive environment variables
        encrypted_env_vars = {}
        for key, value in env_vars.items():
            if key.startswith('DB_') or key.startswith('API_KEY'):
                encrypted_value = cipher_suite.encrypt(value.encode())
                encrypted_env_vars[key] = encrypted_value.decode()
            else:
                encrypted_env_vars[key] = value

        # Create a new directory for the build context
        with tempfile.TemporaryDirectory() as temp_dir:
            # Store the encryption key securely in a file named `.docker_encryption_key` within the build context
            with open(os.path.join(temp_dir, '.docker_encryption_key'), 'wb') as f:
                f.write(encryption_key)

            # Create the Dockerfile content with secure environment variable usage
            dockerfile_content = """
FROM {base_image} as build-stage
WORKDIR /app

# Use a .dockerignore file to exclude sensitive files from the build context
 COPY --from=0 /.dockerignore .
COPY package*.json ./
RUN npm install
COPY . .

RUN npm run build

# Stage 2: Production
FROM {web_server_image}
USER node # Run as non-root user
COPY --from=build-stage /app/dist/static/* /usr/share/nginx/html/
COPY --from=build-stage /app/dist /usr/share/nginx/html/

# Use encrypted environment variables for sensitive information
ENV DB_HOST={db_host}
ENV DB_USER={db_user}
ENV DB_PASSWORD={db_password}

# Example nginx configuration to use the environment variables
COPY nginx.conf /etc/nginx/conf.d/default.conf
WORKDIR /app
CMD ["nginx", "-g", "daemon off;"]
""".format(base_image=base_image, web_server_image=web_server_image,
            db_host=encrypted_env_vars['DB_HOST'], db_user=encrypted_env_vars['DB_USER'],
            db_password=encrypted_env_vars['DB_PASSWORD'])

            # Write the Dockerfile content to a file and handle potential file system errors
            try:
                with open(os.path.join(temp_dir, 'Dockerfile'), 'w') as dockerfile:
                    dockerfile.write(dockerfile_content)
            except OSError as e:
                print("An error occurred while writing to the Dockerfile:", str(e))

        # Copy the build context directory to the current working directory
        shutil.copytree(temp_dir, '.')

    except FileNotFoundError:
        print("The .env file was not found in the current working directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage of generate_dockerfile function
if __name__ == "__main__":
    env_vars = {
        'DB_HOST': secrets.token_urlsafe(16),
        'DB_USER': secrets.token_urlsafe(16),
        'API_KEY': secrets.token_urlsafe(32)
    }
    generate_dockerfile(env_vars)
