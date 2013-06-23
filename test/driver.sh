data=$(cat test/raw.json)
 
rm -rf dest/*

curl --data "$data" http://localhost:8001
