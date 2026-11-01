#!/bin/bash
# Paste this into: claude.ai/code -> your environment -> Settings -> Setup script.
# It runs once per environment (the result is cached for ~7 days); the SessionStart hook in each
# repo's .claude/settings.json pulls updates in the background on top of that.
git clone -q --depth 1 https://github.com/rafaelvtree-lab/claude-config.git "$HOME/.claude-config" \
  && bash "$HOME/.claude-config/install.sh" --cloud \
  || echo "claude-config: install failed (continuing without it)"
