# Note: Python can't directly create a Dockerfile, but we'll write it as if we're writing Node.js code and then translate it into a Dockerfile.

from typing import List

class Dockerfile:
    def __init__(self):
        self.lines = []

    def FROM(self, image: str) -> 'Dockerfile':
        """Set the base image for this build"""
        self.lines.append(f'FROM {image}')
        return self

    def RUN(self, command: str) -> 'Dockerfile':
        """Run a command during the build process."""
        self.lines.append(f'RUN {command}')
        return self

    def COPY(self, src: str, dst: str) -> 'Dockerfile':
        """Copy files from the current directory into the image at the specified destination path"""
        self.lines.append(f'COPY {src} {dst}')
        return self

    def WORKDIR(self, path: str) -> 'Dockerfile':
        """Set the working directory in the container."""
        self.lines.append(f'WORKDIR {path}')
        return self

    def EXPOSE(self, port: int) -> 'Dockerfile':
        """Specify which ports the container exposes to the host."""
        self.lines.append(f'EXPOSE {port}')
        return self

    def ENV(self, key: str, value: str) -> 'Dockerfile':
        """Set environment variables in the image"""
        self.lines.append(f'ENV {key}="{value}"')
        return self

    def CMD(self, command: str) -> 'Dockerfile':
        """Default command to run when the container is started."""
        self.lines.append(f'CMD ["{command}"]')
        return self

    def build(self):
        return '\n'.join(self.lines)


docker = Dockerfile()
docker.FROM('node:lts').WORKDIR('/app').COPY('./package*.json', './').RUN('npm install').EXPOSE(3000).ENV('PORT=3000').CMD('node app.js')

print(docker.build())
