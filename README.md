# Eternal - Vault Hunters Discord bot

![Example of /stats command](https://imgur.com/BQa8iht)

Eternal is a discord bot that allows you to interface with your Vault Hunters Minecraft server. You can view information on any player on the server, such as:

- Vault Level
- Talents / Abilities
- Mod Researches
- Available bounties
- Black Market offerings
- Vault Forge Proficiencies
- Modifiers discovered via Modifier Archives
- Online players

You can also opt in to receiving a ping when you receive new bounties, and having your Discord nickname automatically update to include your current vault level!

## Usage

Start out by using the bot's `/alias` command to supply your Minecraft username. This lets the bot know which player you are when running other commands. With an alias set, you can run most commands (like `/stats`) without having to supply further information. 

With that being said, you can still view information of other players that have not set their alias by supplying their `mc_username` (e.g. `/stats mc_username: Drlegoman`)


## Installation

To use this bot, you'll need to [create your own discord bot](https://discordpy.readthedocs.io/en/stable/discord.html) in the [Discord Developer Portal](https://discord.com/developers/docs/intro). In the URL Generator tab on the Developer portal, check `bot` and `applications.commands`, and give it the permission `Manage Nicknames`. Make sure to copy your bot's token for later when creating it.

It will also require `Python 3.9` or greater, alongside the Python package manager `pip` to be installed on the server.

1. In the terminal, navigate into your Vault Hunters server folder. Clone the bot repository files by running `git clone https://github.com/Lego-RL/eternal-smp-bot.git`. This will put the bot files in a new folder called `eternal-smp-bot`. 

2. Install necessary Python libraries by navigating to the bot folder via `cd eternal-smp-bot`, and run the command `python3 -m pip install -r requirements.txt`. 

3. While still in the `eternal-smp-bot` directory, open the `.env` file in a text editor. Right after `BOT_TOKEN=`, paste the bot token from the Discord bot you generated previously. Optionally, paste your server's IP after `SERVER_IP=` - supplying this solely allows the `/online` command to function to see how many players are online via the website `https://api.mcsrvstat.us`. The IP is not accessed elsewhere.

4. Finally, run the bot! Navigate back to your server folder (with `cd ..` if still in `eternal-smp-bot`) and run `python3 eternal-smp-bot/bot/main.py`. You should see a message that the bot has connected to Discord if all goes well.

5. Over time, the bot may get updated with new features or fix commands that break due to changes with new Vault Hunters updates. To retrieve the most recent version of the bot, you may navigate to the bot folder and run `git pull` to pull new changes. Updates will be announced in the Eternal VH Bot Discord linked below.

## Feedback

If you have any suggestions, feature requests or need help with the installation process feel free to join the [Eternal VH Bot Discord](https://discord.gg/sy3DJkfmHu).

Created by **Lego#0469** with the help of **jayy#6889**.