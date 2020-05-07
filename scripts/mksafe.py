# A script to make a safe example config

import yaml

with open("../config.yaml", "r+") as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

# Replace Discord token
config['discord']['token'] = "Your Discord Token Here"

# Replace oauth string
config['discord']['oauth'] = "Your Oauth Link"

# Disable debugging
config['package', 'debug'] = "false"

# Write to example-config.yaml

with open("../example-config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)