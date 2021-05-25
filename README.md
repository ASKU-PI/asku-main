# Główne repozytorium ASKU

Repozytorium zawiera podmoduły odpoiwadające serwisom, Mavenowy plik .pom będący parentem dla serwisów, a także plik docker-compose oraz zaszyfrowany .env

## Jak uruchomić?

### Backend

1. Sklonuj repozytorium
2. Użyj narzecia git-crypt w celu odszyfrowania .env (klucz wam wysłałem :))
`git-crypt unlock key`
3. Zbuduj pliki .jar każdego serwisu
`./mvnw package -DskipTests`
4. Uruchom docker-compose: `docker-compose up`
