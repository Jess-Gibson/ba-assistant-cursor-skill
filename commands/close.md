---
description: BA Assistant — close out and archive a finished initiative
---
Run the BA Assistant `/close` command (`skills/ba-assistant/sub-skills/ba-initiative-closeout`): confirm the initiative is genuinely done, run the closure retro first, then batch-audit every file in its analysis folder for keep/publish/delete, confirm Confluence is complete, finalise its README, move the folder into the archive tree, and flip `workboard.json` to `archived` so it drops out of daily refresh churn.

One-way and never automatic. Confirm the archive move (step 6) explicitly before executing it — it's the one step here that isn't trivially reversible from chat alone.
