# Docker Case Study - Automate Infra allocation

## Problem Statement
- Dynamic Allocation of Linux systems for users
- Each user should have independent Linux System
- Specific training environment should be created in Container
- User should not allow to access other containers/images
- User should not allow to access docker command
- Monitor participants containers
- Debug/live demo for the participants if they have any doubts/bug in running applications.
- Automate container creation and deletion.

## Solution

We will be using the `ubuntu` image for spawning containers.

### Creation of training environment
The `ubuntu` image might not be sufficient since it lacks many common programs.
We can create a new image with the necessary programs and files and use that for
each user.

- First spawn a new `ubuntu` container and use it's shell by running `docker run --name traincont -it ubuntu /bin/bash`. The container's shell should now be available.
- Make necessary changes like installing new packages and adding new files.
- Exit from the shell by typing the `exit` command.
- The container has now been stopped. We can view it through
`docker container ls -a`.
- We can create a new image from the `traincont` container by running `docker commit traincont training:v1` (`training` is image name and `v1` is its tag).
- The `training` image will be used to create container for each user. This image
can also be pushed onto docker hub so that it can be directly pulled by the users
if required.

### Allocation of container for each user
Now that our image is ready we can create a container for each user. We provide unique container name (can be user id here) so that we can refer
to it afterwards.

To create a container for a single user with user id `abc` the command is: `docker create -it --name abc training:v1 /bin/bash`. This creates
a container with name of `abc` from the image `training:v1`, but doesn't
start the container.

If we are given a file with the list of user ids then we can automate the
allocation of containers. Let the file containing user ids be `userfiles`:

```
user1
user2
user3
user4
user5
```

The script that automates container allocation is `allocate`:

```bash
#!/bin/sh

file=$1

# If filename not passed exit
if [ -z "${file}" ]
then
	echo "Usage: allocate <filename>"
	exit
fi

while read user || [[ -n "$user" ]]
do
	container_id="$(docker create -it --name $user training:v1 /bin/bash)"
	echo "$user: $container_id"
done < "$file"

```

We can run the command `allocate userfiles` to allocate a container for every
user id in `userfiles`.

### Using an allocated container
Now that the container has been allocated for each user we need to start it
and attach the container (attach local standard input, output, and error streams
to the running container).

The container for user with id `abc` can be used by running the following
commands:

```bash
docker start abc # Starts container abc
docker attach abc # Attaches local stdin, stdout and stderr to abc
```

Running the above commands leads to the user getting access to the shell of his
"system".

The user can use the `exit` command to exit from the container. This also stops
the container but the state is preserved. Next time the container is started
it reloads the previous state.

### Safety of containers
Since the resulting shell is a process within a container it is isolated from
the host system and other containers. Any side effects a command or program
might have will only affect the container and not the host system. In general,
we can clearly define what parts of the host system the container can access
when creating or starting the container. The commands mentioned here isolate each
container completely.

The user will also not be able to access the docker command from within the
container. Docker actually creates a UNIX socket and the commands actually
communicate with the docker daemon via the socket. Even if the user installs
`docker` packages the socket is not mounted on the container and so he won't be
able to access the host systems docker daemon.

### Monitoring containers
We can view the resource usage of container `abc` by running the command
`docker stats abc`. This gives an output of the following format:

```
CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT   MEM %               NET I/O             BLOCK I/O           PIDS
aa4fb37ade87        traincont           0.00%               716KiB / 1.952GiB   0.03%               898B / 0B           0B / 0B             1
```

We can also view the logs of container `abc` by running `docker logs abc`. We
can get the real time logs by running `docker logs -f abc`. This follows the log
output and prints every update.

### Deleting containers
Exiting from an attached container only stops the container. But the container
state is still preserved and it can be reloaded easily.

To completely remove the stopped container `abc` we can use the
`docker rm abc` command.

If we have a file containing the list of containers to remove we can automate it
with the script `deallocate`:

```bash
#!/bin/sh

file=$1

if [ -z "${file}" ]
then
	echo "Usage: delete <file>"
	exit
fi

while read user || [[ -n "$user" ]]
do
	docker rm $user
done < "$file"

```

We can use the above script by running `./deallocate userfiles` (`userfiles` has
been described earlier).

### Conclusion

Thus we see that containers provide an efficient way to manage isolated
systems and make it easy to monitor the systems. Isolation provides safety to the
host system and other containers.
