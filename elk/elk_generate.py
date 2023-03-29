import os
import sys
import uuid

def get_log_source():
    print("Please choose a log source:")
    print("1. Local path")
    print("2. Docker container ID")
    choice = input("Enter the number of your choice: ")

    if choice == "1":
        log_path = input("Enter the local path of the logs: ")
        return log_path.strip(), False
    elif choice == "2":
        container_id = input("Enter the Docker container ID: ")
        return container_id.strip(), True
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

def create_docker_compose(log_path, is_container):
    uid = uuid.uuid4()
    volume_string = ""

    if is_container:
        log_path = f"/var/lib/docker/containers/{log_path}/{log_path}-json.log"
        volume_string = f"{log_path}:/logs/log:ro"

    docker_compose = f"""version: '3.8'
services:
  logstash:
    image: docker.elastic.co/logstash/logstash:7.16.2
    volumes:
      - ./logstash-config:/usr/share/logstash/config
      - ./logstash-pipeline:/usr/share/logstash/pipeline
      - {volume_string}
    networks:
      - elk

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.16.2
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - esdata{uid}:/usr/share/elasticsearch/data
    networks:
      - elk

  kibana:
    image: docker.elastic.co/kibana/kibana:7.16.2
    ports:
      - "5601:5601"
    networks:
      - elk

networks:
  elk:
    driver: bridge

volumes:
  esdata{uid}:
"""

    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)

    print("Docker Compose file generated as docker-compose.yml")

def main():
    log_path, is_container = get_log_source()
    create_docker_compose(log_path, is_container)

if __name__ == "__main__":
    main()
