while IFS= read -r line || [[ -n "$line" ]]; do
    heroku config:set "$line" --app pulse-fi
done < "cloud.env"