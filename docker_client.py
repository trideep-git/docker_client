import logging
 
import docker
from docker import errors as errors
 
 
class DockerClient(object):
    __client = None
    __image = None
    __target_registry = None
    __source_registry = None
    __source_registry_username = None
    __source_registry_password = None
    __target_registry_username = None
    __target_registry_password = None
 
    def __init__(self):
        self.__client = docker.from_env()
 
    def get_client(self):
        return self.__client
 
    def login(self, username, password, registry):
        logging.info("Logging in to docker registry {}".format(registry))
        self.__client.login(username=username, password=password, registry=registry)
 
    def pull_image(self, source_registry, image_name):
        self.__image = self.__client.images.pull(source_registry + "/" + image_name)
        logging.debug("Image id is {}".format(self.__image.id))
 
    def push_image(self, image_name, auth_config, target_registry):
        tag_name = target_registry + "/" + image_name
        if self.__tag_image(tag_name):
            generator = self.__client.images.push(repository=tag_name, auth_config=auth_config)
            logging.debug("{}".format(generator))
        else:
            logging.warn("Image not tagged and pushed")
 
    def __tag_image(self, tag_name):
        return self.__image.tag(tag_name)
 
    def promote_image(self, docker_config, deployment_name):
        try:
            logging.debug("Promoting image for {}".format(deployment_name))
            self.login(self.__source_registry_username, self.__source_registry_password, self.__source_registry)
            if 'image_name' in docker_config and docker_config['image_name']:
                logging.debug("pulling docker image {} for {}".format(docker_config['image_name'], deployment_name))
                self.pull_image(self.__source_registry, docker_config['image_name'])
                logging.debug("Image {} pulled".format(docker_config['image_name']))
                target_auth_config = {
                    'username': self.__target_registry_username,
                    'password': self.__target_registry_password
                }
                self.push_image(docker_config['image_name'], target_auth_config, self.__target_registry)
                logging.debug("Image {} pushed".format(docker_config['image_name']))
            else:
                raise KeyError("image_name not found for docker promotion for {}".format(deployment_name))
        except errors.APIError:
            raise
 
    def validate_docker_parameters(self, options):
        try:
            self.__source_registry = options.source_registry
        except Exception as e:
            logging.error("Error getting source_registry for docker promotion params {}".format(e), exc_info=True)
            raise
 
        try:
            self.__source_registry_username = options.source_registry_username
        except Exception as e:
            logging.error("Error getting source_registry_username docker promotion params {}".format(e), exc_info=True)
            raise
 
        try:
            self.__source_registry_password = options.source_registry_password
        except Exception as e:
            logging.error("Error getting source_registry_password docker promotion params {}".format(e), exc_info=True)
            raise
 
        try:
            self.__target_registry = options.target_registry
        except Exception as e:
            logging.error("Error getting target_registry docker promotion params {}".format(e), exc_info=True)
            raise
 
        try:
            self.__target_registry_username = options.target_registry_username
        except Exception as e:
            logging.error("Error getting target_registry_username docker promotion params {}".format(e), exc_info=True)
            raise
 
        try:
            self.__target_registry_password = options.target_registry_password
        except Exception as e:
            logging.error("Error getting target_registry_password docker promotion params {}".format(e), exc_info=True)
            raise
 
if __name__ == "__main__":
    username = 'analytics_dev_01'
    password = 'analytics_dev_01'
    source_registry = 'buildregistry.na03.bhge.com'
    target_registry = 'registryqa.na03.bhge.com'
    image_name = 'add_nums:latest'

    target_auth_config = {
        'username': username,
        'password': password
    }
    try:
        docker_client = DockerClient()
        docker_client.login(username, password, source_registry)
        docker_client.pull_image(source_registry, image_name)
        docker_client.push_image(image_name, target_auth_config, source_registry, target_registry)
        # logging.info("all images {}".format(docker_client.get_client().images.list()))
    except errors.APIError as e:
        logging.error("{}".format(e), exc_info=True)
        raise
 
