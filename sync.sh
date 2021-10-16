#!/bin/bash
LIGHT_BLUE='\033[1;34m'
GREEN='\033[0:32m'
NC='\033[0m' # No Color

printf "${LIGHT_BLUE} \nSETTING ENV VARIABLES...\n\n${NC}"
export $(grep -v '^#' .env | xargs)

git config --global credential.helper "cache --timeout=3600"

printf "${LIGHT_BLUE} \nPULLING REPOS...\n\n${NC}"

printf "${LIGHT_BLUE} \nASKU-MAIN...\n\n${NC}"
git checkout main && git pull

printf "${LIGHT_BLUE} \nASKU-AUTH-SERVICE...\n\n${NC}"
cd asku-auth-service && git checkout main && git pull && cd ..

printf "${LIGHT_BLUE} \nASKU-CLOUD...\n\n${NC}"
cd asku-cloud && git checkout main && git pull && cd ..

printf "${LIGHT_BLUE} \nASKU-CONFIG...\n\n${NC}"
cd asku-config && git checkout main && git pull && cd ..

printf "${LIGHT_BLUE} \nASKU-IMAGE-SERVICE..\n\n${NC}"
cd asku-image-service && git checkout master && git pull && cd ..

printf "${LIGHT_BLUE} \nASKU-MAGAZINE-SERVICE...\n\n${NC}"
cd asku-magazine-service && git checkout main && git pull && cd ..

printf "${LIGHT_BLUE} \nBUILDING DOCKER IMAGES...\n\n${NC}"
docker compose build

printf "${GREEN} \nDONE!!! YOU CAN NOW LAUNCH THE SERVICES WITH docker compose up\n${NC}"