This is a great initiative. Since you're targeting users who are "starting very fresh" and may not be tech-savvy, I have designed this `INSTALLATION.md` to be extremely visual, using clear emojis, step-by-step checkboxes, and plain-English explanations for technical terms.

Below is the content for your file.

---

# 🚀 E*Trade MCP Server: Simple Installation Guide

Welcome! This guide will help you connect your E*Trade account to AI tools like **Claude** or **Gemini**. Once finished, you can ask your AI things like *"Show my portfolio"* or *"Analyze my Trust account risk."*

---

## 🛠 Prerequisites (Do these first!)

1. **Get E*Trade API Keys:**
* Go to [E*Trade Developer Portal](https://developer.etrade.com/home).
* Follow their steps to get your **Consumer Key** and **Consumer Secret**.
* *Think of these as your "Digital ID" for the AI to talk to E*Trade.*


2. **Install "GitHub CLI" (gh):**
* If you don't have it, download it [here](https://cli.github.com/). This tool lets you download the code easily.



---

## 📂 Step 1: Download the Code

Open your **Terminal** (on Mac, press `Cmd + Space` and type "Terminal") and copy-paste these lines one by one:

1. **Create a folder for the project:**
```bash
mkdir $HOME/mcp
cd $HOME/mcp

```


2. **Download the software:**
```bash
gh repo clone shahid11885/etradeMCP

```



---

## 🔑 Step 2: Add Your Secret Keys

Now we need to tell the software who you are.

1. Navigate to the config folder: `cd $HOME/mcp/etradeMCP/config`
2. Look for a file named `config.ini.example`.
3. **Rename it** to `config.ini`.
4. Open it with a text editor and paste your **Consumer Key** and **Consumer Secret** from E*Trade into the matching spots.

---

## ⚡ Step 3: Prepare the System

Run these two commands in your Terminal. They do the "heavy lifting" to set everything up.

1. **One-time Setup:** (Sets up the environment)
```bash
./setup_env.sh

```


2. **Daily Login:** (Connects your account)
```bash
./etrade-auth.sh

```


> 💡 **Note:** You will need to run `./etrade-auth.sh` once every day you plan to use the tool, as E*Trade's connection expires daily for your security.



---

## 🤖 Step 4: Tell your AI to use E*Trade

You need to "plug" the server into your favorite AI app.

### For Gemini Users

Open the file `$HOME/.gemini/settings.json` and paste this inside the `mcpServers` section:

```json
"etrade": {
  "command": "$HOME/mcp/etradeMCP/venv/bin/python",
  "args": ["$HOME/mcp/etradeMCP/src/mcp/server.py"],
  "env": {
    "PYTHONPATH": "$HOME/mcp/etradeMCP/"
  }
}

```

### For Claude Desktop Users

Open the file `$HOME/Library/Application Support/Claude/claude_desktop_config.json` and paste this inside the `mcpServers` section:

```json
"etrade": {
  "command": "$HOME/mcp/etradeMCP/venv/bin/python",
  "args": ["$HOME/mcp/etradeMCP/src/mcp/server.py"],
  "env": {
    "PYTHONPATH": "$HOME/mcp/etradeMCP/"
  }
}

```

---

## ✅ Step 5: Test it out!

Restart your Claude or Gemini app. Type the following to see if it works:

* *"Show my E*Trade balance"*
* *"What are my current holdings?"*

---

## 📈 The "Pro" Analysis Prompt

Once you are set up, copy and paste the prompt below to get a professional-grade analysis of your **Trust Account**.

> **Copy-Paste this into the AI:**
> *"You are my portfolio analyst. Use the ETrade MCP to analyze my Trust account. Perform a deep risk analysis, suggest downside hedging using QQQ if needed, and design a low-risk covered call program that prioritizes growth and avoids triggering taxes. Provide a Snapshot, Exposure Map, and a 90-day execution plan."*

---

### ❓ Troubleshooting

* **Permissions:** if a command fails, ensure you are logged into E*Trade via the `./etrade-auth.sh` command.
* **Pathing:** Ensure you created the folder in `$HOME/mcp` as instructed.

---


