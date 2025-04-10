all: build

clean:
	@rm -rf ./build/
	@rm -rf ./main-backend.docker.tar

build: clean
	@python compiletopyc.py -s ./apps
	@python compiletopyc.py -s ./project
	@cp manage.py ./build/
	@cp requirements.txt ./build/
	@cp Dockerfile ./build/
	@cp project/*.py ./build/project/
	@rm -f ./build/project/local_settings.pyc

docker: build
	@cd ./build && docker build -t tkliuxing/main-backend .
	@docker save tkliuxing/main-backend:latest -o ./main-backend.docker.tar

test:
	@ssh root@main.test.nmhuixin.com "/root/um.sh"