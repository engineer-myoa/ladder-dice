import configparser

config = configparser.ConfigParser()
config.read("app.config", "utf-8")
print(config.get("TOKEN", "slack.api.token"))