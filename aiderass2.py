import os
from modelscraper import ModelInfoScraper
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
from semantic_text_splitter import TextSplitter  # Added for better text chunking

load_dotenv()

def get_optimal_model(text_length):
    """Select the most cost-effective model based on text length and complexity"""
    if text_length < 2000:
        return "gpt-3.5-turbo"  # Cheapest option for short texts
    elif text_length < 6000:
        return "claude-3-sonnet-20240229"  # Good balance for medium texts
    else:
        return "gpt-4-turbo"  # Most capable for complex tasks

def semantic_chunk_text(text, max_chunk_size=4000):
    """Split text into semantic chunks using semantic-text-splitter"""
    splitter = TextSplitter(max_chunk_size)
    return splitter.chunks(text)

def process_text_in_chunks(client, text, system_prompt, model=None):
    """Process text in semantically meaningful chunks with optimal model selection"""
    if not model:
        model = get_optimal_model(len(text))
    
    chunks = semantic_chunk_text(text)
    all_results = []
    
    for i, chunk in enumerate(chunks):
        messages = [
            {"role": "system", "content": system_prompt},  # system_prompt should be a string
            {"role": "user", "content": f"Part {i+1}/{len(chunks)}: {chunk}"}
        ]
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0,
                stream=True  # Enable streaming for faster responses
            )
            
            chunk_result = ""
            for part in response:
                if hasattr(part.choices[0].delta, 'content'):
                    chunk_result += part.choices[0].delta.content or ""
            
            all_results.append(chunk_result)
            
        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            # Fallback to a more stable model if error occurs
            if model != "gpt-3.5-turbo":
                return process_text_in_chunks(client, chunk, system_prompt, "gpt-3.5-turbo")
    
    return "\n".join(all_results)

# Initialize clients with error handling
try:
    scraper = ModelInfoScraper()
    latest_models = scraper.get_latest_models()

    client_anthropic = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    client_openai = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        max_retries=3  # Add retry logic
    )

except Exception as e:
    print(f"Error initializing clients: {str(e)}")
    exit(1)

def main():
    # Fix the system prompt format - just use the content string directly
    system_prompt = "You are an AI assistant specialized in helping users set up and optimize their configuration file for the Aider tool. Your task is to analyze the user's current configuration (if available), provide recommendations for improvement, and address any specific queries they may have about setting up Aider."
    
    # Your text content and system prompt
    text_content = [
        {
            "role": "user",
            "content": "<examples>\n<example>\n<USER_QUERY>\nWhat are the commands for aider.\n</USER_QUERY>\n<CONFIG_FILE_PATH>\n/Users/markcarpenter/Desktop/Melbudget/.aider.conf.yml or /Users/markcarpenter/.aider.conf.yml\n</CONFIG_FILE_PATH>\n<ideal_output>\n<thought_process>\nTo provide a comprehensive answer about the commands for Aider, I need to consider the following:\n\n1. Identify key components of a .aider.conf.yaml file:\n   - The configuration file is not directly related to the commands, but it's important to note its potential locations.\n\n2. The file doesn't exist in this case, so we'll focus on the commands themselves.\n\n3. Analyze how the command list aligns with the user's specific query:\n   - The user wants to know about Aider commands, so we need to provide a complete list of available commands and options.\n\n4. Plan clear, step-by-step instructions:\n   - We'll start with the basic usage syntax.\n   - Then, we'll group the commands by their functions (e.g., Main, Model Settings, Cache Settings, etc.).\n   - For each group, we'll list the relevant commands and their descriptions.\n\n5. Explain the purpose and impact of each command option:\n   - We'll..."
        },
        {
            "role": "user",
            "content": "please - update this code based on spending the least amount of money and getting the most amount of production - ##########################################################\n# Sample .aider.conf.yml\n# This file lists *all* the valid configuration entries.\n# Place in your home dir, or at the root of your git repo.\n##########################################################\n\n# Note: You can only put OpenAI and Anthropic API keys in the yaml\n# config file. Keys for all APIs can be stored in a .env file\n# https://aider.chat/docs/config/dotenv.html\n\n##########\n# options:\n\n## show this help message and exit\n#help: xxx\n\n#######\n# Main:\n\n## Specify the OpenAI API key\nopenai-api-key: ${OPENAI_API_KEY}\n\n## Specify the Anthropic API key\nanthropic-api-key: ${ANTHROPIC_API_KEY}\n\n## Specify the model to use for the main chat\nmodel: ${MODEL}\n\n## Use claude-3-opus-20240229 model for the main chat\nopus: ${OPUS}\n\n## Use claude-3-5-sonnet-20241022 model for the main chat\nsonnet: ${SONNET}\n\n## Use gpt-4-0613 model for the main chat\n4: ${GPT4}\n\n## Use gpt-4o-2024-08-06 model for the main chat\n4o: ${GPT4O}\n\n## Use gpt-4o-mini model for the main chat\nmini: ${MINI}\n\n## Use gpt-4-1106-preview model for the main chat\n4-turbo: ${GPT4_TURBO}\n\n## Use gpt-3.5-turbo model for the main chat\n35turbo: ${GPT35_TURBO}\n\n## Use deepseek/deepseek-coder model for the main chat\ndeepseek: ${DEEPSEEK}\n\n## Use o1-mini model for the main chat\no1-mini: ${O1_MINI}\n\n## Use o1-preview model for the main chat\no1-preview: ${O1_PREVIEW}\n\n#################\n# Model Settings:\n\n## List known models which match the (partial) MODEL name\nlist-models: ${LIST_MODELS}\n\n## Specify the api base url\nopenai-api-base: ${OPENAI_API_BASE}\n\n## Specify the api_type\nopenai-api-type: ${OPENAI_API_TYPE}\n\n## Specify the api_version\nopenai-api-version: ${OPENAI_API_VERSION}\n\n## Specify the deployment_id\nopenai-api-deployment-id: ${OPENAI_API_DEPLOYMENT_ID}\n\n## Specify the OpenAI organization ID\nopenai-organization-id: ${OPENAI_ORGANIZATION_ID}\n\n## Specify a file with aider model settings for unknown models\nmodel-settings-file: ${MODEL_SETTINGS_FILE}\n\n## Specify a file with context window and costs for unknown models\nmodel-metadata-file: ${MODEL_METADATA_FILE}\n\n## Verify the SSL cert when connecting to models (default: True)\nverify-ssl: ${VERIFY_SSL}\n\n## Specify what edit format the LLM should use (default depends on model)\nedit-format: ${EDIT_FORMAT}\n\n## Use architect edit format for the main chat\narchitect: ${ARCHITECT}\n\n## Specify the model to use for commit messages and chat history summarization (default depends on --model)\nweak-model: ${WEAK_MODEL}\n\n## Specify the model to use for editor tasks (default depends on --model)\neditor-model: ${EDITOR_MODEL}\n\n## Specify the edit format for the editor model (default: depends on editor model)\neditor-edit-format: ${EDITOR_EDIT_FORMAT}\n\n## Only work with models that have meta-data available (default: True)\nshow-model-warnings: ${SHOW_MODEL_WARNINGS}\n\n## Soft limit on tokens for chat history, after which summarization begins. If unspecified, defaults to the model's max_chat_history_tokens.\nmax-chat-history-tokens: ${MAX_CHAT_HISTORY_TOKENS}\n\n## Specify the .env file to load (default: .env in git root)\nenv-file: ${ENV_FILE}\n\n#################\n# Cache Settings:\n\n## Enable caching of prompts (default: False)\ncache-prompts: ${CACHE_PROMPTS}\n\n## Number of times to ping at 5min intervals to keep prompt cache warm (default: 0)\ncache-keepalive-pings: ${CACHE_KEEPALIVE_PINGS}\n\n###################\n# Repomap Settings:\n\n## Suggested number of tokens to use for repo map, use 0 to disable (default: 1024)\nmap-tokens: ${MAP_TOKENS}\n\n## Control how often the repo map is refreshed. Options: auto, always, files, manual (default: auto)\nmap-refresh: ${MAP_REFRESH}\n\n## Multiplier for map tokens when no files are specified (default: 2)\nmap-multiplier-no-files: ${MAP_MULTIPLIER_NO_FILES}\n\n################\n# History Files:\n\n## Specify the chat input history file (default: .aider.input.history)\ninput-history-file: ${INPUT_HISTORY_FILE}\n\n## Specify the chat history file (default: .aider.chat.history.md)\nchat-history-file: ${CHAT_HISTORY_FILE}\n\n## Restore the previous chat history messages (default: False)\nrestore-chat-history: ${RESTORE_CHAT_HISTORY}\n\n## Log the conversation with the LLM to this file (for example, .aider.llm.history)\nllm-history-file: ${LLM_HISTORY_FILE}\n\n##################\n# Output Settings:\n\n## Use colors suitable for a dark terminal background (default: False)\ndark-mode: ${DARK_MODE}\n\n## Use colors suitable for a light terminal background (default: False)\nlight-mode: ${LIGHT_MODE}\n\n## Enable/disable pretty, colorized output (default: True)\npretty: ${PRETTY}\n\n## Enable/disable streaming responses (default: True)\nstream: ${STREAM}\n\n## Set the color for user input (default: #00cc00)\nuser-input-color: ${USER_INPUT_COLOR}\n\n## Set the color for tool output (default: None)\ntool-output-color: ${TOOL_OUTPUT_COLOR}\n\n## Set the color for tool error messages (default: #FF2222)\ntool-error-color: ${TOOL_ERROR_COLOR}\n\n## Set the color for tool warning messages (default: #FFA500)\ntool-warning-color: ${TOOL_WARNING_COLOR}\n\n## Set the color for assistant output (default: #0088ff)\nassistant-output-color: ${ASSISTANT_OUTPUT_COLOR}\n\n## Set the color for the completion menu (default: terminal's default text color)\ncompletion-menu-color: ${COMPLETION_MENU_COLOR}\n\n## Set the background color for the completion menu (default: terminal's default background color)\ncompletion-menu-bg-color: ${COMPLETION_MENU_BG_COLOR}\n\n## Set the color for the current item in the completion menu (default: terminal's default background color)\ncompletion-menu-current-color: ${COMPLETION_MENU_CURRENT_COLOR}\n\n## Set the background color for the current item in the completion menu (default: terminal's default text color)\ncompletion-menu-current-bg-color: ${COMPLETION_MENU_CURRENT_BG_COLOR}\n\n## Set the markdown code theme (default: default, other options include monokai, solarized-dark, solarized-light)\ncode-theme: ${CODE_THEME}\n\n## Show diffs when committing changes (default: False)\nshow-diffs: ${SHOW_DIFFS}\n\n###############\n# Git Settings:\n\n## Enable/disable looking for a git repo (default: True)\ngit: ${GIT}\n\n## Enable/disable adding .aider* to .gitignore (default: True)\ngitignore: ${GITIGNORE}\n\n## Specify the aider ignore file (default: .aiderignore in git root)\naiderignore: ${AIDERIGNORE}\n\n## Only consider files in the current subtree of the git repository\nsubtree-only: ${SUBTREE_ONLY}\n\n## Enable/disable auto commit of LLM changes (default: True)\nauto-commits: ${AUTO_COMMITS}\n\n## Enable/disable commits when repo is found dirty (default: True)\ndirty-commits: ${DIRTY_COMMITS}\n\n## Attribute aider code changes in the git author name (default: True)\nattribute-author: ${ATTRIBUTE_AUTHOR}\n\n## Attribute aider commits in the git committer name (default: True)\nattribute-committer: ${ATTRIBUTE_COMMITTER}\n\n## Prefix commit messages with 'aider: ' if aider authored the changes (default: False)\nattribute-commit-message-author: ${ATTRIBUTE_COMMIT_MESSAGE_AUTHOR}\n\n## Prefix all commit messages with 'aider: ' (default: False)\nattribute-commit-message-committer: ${ATTRIBUTE_COMMIT_MESSAGE_COMMITTER}\n\n## Commit all pending changes with a suitable commit message, then exit\ncommit: ${COMMIT}\n\n## Specify a custom prompt for generating commit messages\ncommit-prompt: ${COMMIT_PROMPT}\n\n## Perform a dry run without modifying files (default: False)\ndry-run: ${DRY_RUN}\n\n## Skip the sanity check for the git repository (default: False)\nskip-sanity-check-repo: ${SKIP_SANITY_CHECK_REPO}\n\n########################\n# Fixing and committing:\n\n## Lint and fix provided files, or dirty files if none provided\nlint: ${LINT}\n\n## Specify lint commands to run for different languages, eg: \"python: flake8 --select=...\" (can be used multiple times)\nlint-cmd: ${LINT_CMD}\n## Specify multiple values like this:\nlint-cmd:\n  - ${LINT_CMD_1}\n  - ${LINT_CMD_2}\n  - ${LINT_CMD_3}\n\n## Enable/disable automatic linting after changes (default: True)\nauto-lint: ${AUTO_LINT}\n\n## Specify command to run tests\ntest-cmd: ${TEST_CMD}\n\n## Enable/disable automatic testing after changes (default: False)\nauto-test: ${AUTO_TEST}\n\n## Run tests and fix problems found\ntest: ${TEST}\n\n#################\n# Other Settings:\n\n## specify a file to edit (can be used multiple times)\nfile: ${FILE}\n## Specify multiple values like this:\nfile:\n  - ${FILE_1}\n  - ${FILE_2}\n  - ${FILE_3}\n\n## specify a read-only file (can be used multiple times)\nread: ${READ}\n## Specify multiple values like this:\nread:\n  - ${READ_1}\n  - ${READ_2}\n  - ${READ_3}\n\n## Use VI editing mode in the terminal (default: False)\nvim: ${VIM}\n\n## Specify the language to use in the chat (default: None, uses system settings)\nchat-language: ${CHAT_LANGUAGE}\n\n## Show the version number and exit\nversion: ${VERSION}\n\n## Check for updates and return status in the exit code\njust-check-update: ${JUST_CHECK_UPDATE}\n\n## Check for new aider versions on launch\ncheck-update: ${CHECK_UPDATE}\n\n## Install the latest version from the main branch\ninstall-main-branch: ${INSTALL_MAIN_BRANCH}\n\n## Upgrade aider to the latest version from PyPI\nupgrade: ${UPGRADE}\n\n## Apply the changes from the given file instead of running the chat (debug)\napply: ${APPLY}\n\n## Always say yes to every confirmation\nyes-always: ${YES_ALWAYS}\n\n## Enable verbose output\nverbose: ${VERBOSE}\n\n## Print the repo map and exit (debug)\nshow-repo-map: ${SHOW_REPO_MAP}\n\n## Print the system prompts and exit (debug)\nshow-prompts: ${SHOW_PROMPTS}\n\n## Do all startup activities then exit before accepting user input (debug)\nexit: ${EXIT}\n\n## Specify a single message to send the LLM, process reply then exit (disables chat mode)\nmessage: ${MESSAGE}\n\n## Specify a file containing the message to send the LLM, process reply, then exit (disables chat mode)\nmessage-file: ${MESSAGE_FILE}\n\n## Specify the encoding for input and output (default: utf-8)\nencoding: ${ENCODING}\n\n## Specify the config file (default: search for .aider.conf.yml in git root, cwd or home directory)\nconfig: ${CONFIG}\n\n## Run aider in your browser\ngui: ${GUI}\n\n## Enable/disable suggesting shell commands (default: True)\nsuggest-shell-commands: ${SUGGEST_SHELL_COMMANDS}\n\n## Enable/disable fancy input with history and completion (default: True)\nfancy-input: ${FANCY_INPUT}\n\n#################\n# Voice Settings:\n\n## Audio format for voice recording (default: wav). webm and mp3 require ffmpeg\nvoice-format: ${VOICE_FORMAT}\n\n## Specify the language for voice using ISO 639-1 code (default: auto)\nvoice-language: ${VOICE_LANGUAGE}\n\n"
        }
    ]

    try:
        # Convert the list of dictionaries to a string format
        formatted_text = "\n".join(msg["content"] for msg in text_content)
        
        # Process the text in chunks with optimal model selection
        result = process_text_in_chunks(client_openai, formatted_text, system_prompt)
        print(result)
    
    except Exception as e:
        print(f"Error in main processing: {str(e)}")

if __name__ == "__main__":
    main()
