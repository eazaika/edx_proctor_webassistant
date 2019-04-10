#!/bin/bash -e
# by Evgeniy Bondarenko <Bondarenko.Hub@gmail.com>
# last changes 08.11.2018 Updated


dockerhub=${dockerhub:-"docker.u2035s.ru"}
name=${name:-"unti/epw"}
tag=${tag:-"stage"}
NO_CACHE=${NO_CACHE:-"random"}
targets=${targets:-"base notifications"}
gitbranch=${gitbranch:-$(git rev-parse --abbrev-ref HEAD | cut -f2 -d/)}
start_build=${start_build:-$(date +%Y-%m-%d_%H-%M-%S)}
version="_${start_build}_${gitbranch}"

for target in ${targets}
do

if [ "${target}" == "base" ]; then
    name_tmp=${name}
    name=${name}
else
    name_tmp=${name}
    name=${name}-${target}
fi


docker build --target $target  --build-arg NO_CACHE=${NO_CACHE}  -t ${dockerhub}/${name}:latest -t ${dockerhub}/${name}:${tag} -t ${dockerhub}/${name}:${tag}${version}  .

if [ ${tag} == 'prod' ]; then
docker push ${dockerhub}/${name}:${tag}${version} && docker push ${dockerhub}/${name}:${tag}
else
docker push ${dockerhub}/${name}:${tag} && docker push ${dockerhub}/${name}:latest
fi
name=${name_tmp}
done