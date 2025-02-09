Han SC2 Bot - ML Based Bot

Use ML to make decisions based on the current state of the game.

[205-02-09] Initial code based on claude.ai.

My prompts:

- want to write a bot to play starcraft2, and use machine learning, how to do that?
- can you use python-sc2 library instead of pysc2 lib?
- improve the bot that can keep improving the model by running many games.
- I didn't see on_step function. also didn't see how reward are used. could you fix the issues.
- AttributeError: 'SC2MLBot' object has no attribute '_build_or_load_model'. please fix the issue.

There are some importing errors and use async for main function, which needs to be fixed. otherwise mostly good.

The initial ML bot is dumb. actions needs to be improved.







