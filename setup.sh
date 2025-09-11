#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

# ANSI styling
bold=$(tput bold)
blue=$(tput setaf 4)
green=$(tput setaf 2)
magenta=$(tput setaf 5)
red=$(tput setaf 1)
reset=$(tput sgr0)
yellow=$(tput setaf 3)

# UI charset init (fallback if no UTF-8 or forced)
USE_ASCII=0
if [[ ${UNZIP_BOT_ASCII:-0} -eq 1 ]]; then
  USE_ASCII=1
elif [[ ${LANG:-} != *UTF-8* && ${LC_CTYPE:-} != *UTF-8* ]]; then
  USE_ASCII=1
fi
[[ $TERM == "dumb" ]] && USE_ASCII=1

init_ui_chars() {
  if [[ $USE_ASCII -eq 1 ]]; then
    TL='+' TR='+' BL='+' BR='+' H='-' V='|'
  else
    TL='╭' TR='╮' BL='╰' BR='╯' H='─' V='│'
  fi
}
init_ui_chars

# width helpers
# Return 0 (false) / 1 (true) in $? whether codepoint is wide (2 columns)
is_wide() {
  local codepoint=$1
  # East Asian Wide / Fullwidth core ranges + common emoji blocks (no ambiguous)
  if ((codepoint>=0x1100 && codepoint<=0x115F))  || \
     ((codepoint>=0x2329 && codepoint<=0x232A))  || \
     ((codepoint>=0x2E80 && codepoint<=0x303E))  || \
     ((codepoint>=0x3040 && codepoint<=0xA4CF))  || \
     ((codepoint>=0xAC00 && codepoint<=0xD7A3))  || \
     ((codepoint>=0xF900 && codepoint<=0xFAFF))  || \
     ((codepoint>=0xFE10 && codepoint<=0xFE19))  || \
     ((codepoint>=0xFE30 && codepoint<=0xFE6F))  || \
     ((codepoint>=0xFF00 && codepoint<=0xFF60))  || \
     ((codepoint>=0xFFE0 && codepoint<=0xFFE6))  || \
     ((codepoint>=0x1F300 && codepoint<=0x1F64F)) || \
     ((codepoint>=0x1F900 && codepoint<=0x1F9FF)); then
    return 0
  fi
  return 1
}

is_zero_width() {
  local codepoint=$1
  # VS16, ZWJ, skin tone modifiers
  if (( codepoint==0xFE0F || codepoint==0x200D || (codepoint>=0x1F3FB && codepoint<=0x1F3FF) )); then
    return 0
  fi
  return 1
}

# Draw a box around text
print_box() {
  local txt="$1"
  local color="${2:-}"
  # split into lines
  mapfile -t lines <<<"$txt"
  declare -a disp_lens
  # compute maximum line length
  local max=0

  for line in "${!lines[@]}"; do
    local raw="${lines[line]}"
    local disp=0

    # read each code‑point
    while IFS= read -r -n1 ch; do
      [[ -z $ch ]] && break

      # codepoint integer
      local code
      code=$(printf '%d' "'$ch")

      # skip zero‑width joiner
      if is_zero_width "$code"; then
        continue
      fi

      if is_wide "$code"; then
        ((disp+=2))
      else
        ((disp++))
      fi
    done <<<"$raw"

    disp_lens[line]=$disp
    ((disp>max)) && max=$disp
  done

  local inner=$max
  local border=$((inner + 4))

  # top border
  if [[ $USE_ASCII -eq 1 ]]; then
    printf "\n${bold}${color}%s" "$TL"
    printf "%*s" "$((border-2))" "" | tr ' ' "$H"
    printf "%s\n" "$TR"
  else
    printf "\n${bold}${color}%s%*s%s\n" "$TL" "$((border-2))" '' "$TR" | tr ' ' "$H"
  fi

  # centered lines
  for i in "${!lines[@]}"; do
    local line="${lines[i]}"
    local dlen=${disp_lens[i]}
    local pad=$((inner - dlen))
    ((pad<0)) && pad=0
    local left=$((pad / 2))
    local right=$((pad - left))
    printf "%s${reset}%*s%s%*s${color}%s\n" "$V" $((left + 1)) "" "$line" $((right + 1)) "" "$V"
  done

  # bottom border
  if [[ $USE_ASCII -eq 1 ]]; then
    printf "%s" "$BL"
    printf "%*s" "$((border-2))" "" | tr ' ' "$H"
    printf "%s${reset}\n\n" "$BR"
  else
    printf "%s%*s%s${reset}\n\n" "$BL" "$((border-2))" '' "$BR" | tr ' ' "$H"
  fi
}

# Validate variable against regex
validate_var() {
  local name="$1" value="$2" regex="$3"

  if [[ ! "$value" =~ $regex ]]; then
    print_box "❌ Error : invalid $name [ $value ]" "${red}"
    exit 1
  fi
}

# Prompt for input with default and optional non-empty validation
prompt_input() {
  local prompt="$1" default="$2" allow_empty="${3:-false}" val

  while true; do
    if [[ -n "$default" ]]; then
      read -e -rp "$prompt [ ${green}$default${reset} ] : " val
      val="${val:-$default}"
    else
      read -e -rp "$prompt : " val
    fi

    # if empty allowed or value non-empty, accept
    if [[ "$allow_empty" == "true" ]] || [[ -n "$val" ]]; then
      echo "$val"
      return
    fi

    echo "${red}❗ Value cannot be empty${reset}"
  done
}

# Prompt for yes/no with arrow keys
prompt_confirm() {
  local opts=(Yes No)
  local cursor=0
  local key rest

  while true; do
    # display current choice
    local left=${opts[0]} right=${opts[1]}
    if ((cursor == 0)); then
      printf "\r${bold}[ ${green}%s${reset}${bold} / %s ]${reset}" "$left" "$right"
    else
      printf "\r${bold}[ %s / ${green}%s${reset}${bold} ]${reset}" "$left" "$right"
    fi

    # read one character
    IFS= read -rsn1 key
    # if it's ESC, try to read two more bytes (arrow keys)
    if [[ $key == $'\x1b' ]]; then
      read -rsn2 -t 0.1 rest
      key+=$rest
    fi

    case "$key" in
    # → or ↓
    $'\x1b[C' | $'\x1b[B') ((cursor = (cursor + 1) % 2)) ;;
    # ← or ↑
    $'\x1b[D' | $'\x1b[A') ((cursor = (cursor + 1) % 2)) ;;
    # Enter
    "") break ;;
    # anything else: ignore
    *) ;;
    esac
  done

  printf "\n"
  [[ "${opts[cursor]}" == "Yes" ]]
}

# Early exit if the script is run as root
if [[ $EUID -eq 0 ]]; then
  print_box "❌ Error : script cannot be run as root" "${red}"
  exit 1
fi

# Parse flags : require -a|--ci for other params
CI_MODE=false

for arg in "$@"; do [[ "$arg" =~ ^(-a|--ci)$ ]] && CI_MODE=true; done

# Defaults
ARG_DIR=false
ARG_FOLDER=false
ARG_ENV=false
ARG_GIT=false

DIR="$HOME/"
FOLDER="unzip-bot-EDM115"
ENV_FILE=""
GIT_URL="https://github.com/EDM115/unzip-bot.git"
WORKING_DIR=$(pwd)

# Argument parsing
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h | --help)
    print_box $'ℹ️ Usage : setup.sh [options]\n\n⚙️ Options :\n-a|--ci • Run in CI mode (automated)\n-e|--env • Path to env file (required in CI mode)\n-d|--destination • Directory to clone into (current/home)\n-f|--foldername • Folder name to clone into\n-g|--git • Git repository URL\n-h|--help • Display this help message' "${blue}"
    exit 0
    ;;
  -a | --ci)
    shift
    ;;
  -e | --env)
    ENV_FILE="$2"
    ARG_ENV=true
    shift 2
    ;;
  -d | --destination)
    case "$2" in
    current) DIR=$(realpath ".") ;; home) DIR=$(realpath "~") ;;
    *)
      print_box '❌ Error : -d|--destination must be "current" or "home"' "${red}"
      exit 1
      ;;
    esac

    ARG_DIR=true
    shift 2
    ;;
  -f | --foldername)
    FOLDER=$(realpath "$2")
    ARG_FOLDER=true
    shift 2
    ;;
  -g | --git)
    GIT_URL="$2"
    ARG_GIT=true
    shift 2
    ;;
  *)
    print_box "❓ Unknown option : $1" "${red}"
    exit 1
    ;;
  esac
done

# 1) Welcome & confirm
print_box $'⚡ unzip-bot setup script ⚡\n💻 By EDM115 💻\n\nThis script allows you to easily set up the unzip-bot on your VPS !' "${blue}"
printf "%sℹ️ Automated usage available, run with -h|--help for more info%s\n\n" "${magenta}" "${reset}"

if $CI_MODE; then
  printf "%s‼️ CI mode : proceeding without confirmation%s\n\n" "${red}" "${reset}"
else
  printf "%s❓ Proceed with setup ?%s\n" "${blue}" "${reset}"
  prompt_confirm || {
    print_box "❌ Setup aborted" "${red}"
    exit 0
  }
fi

printf "\n%s--- ⚙️ Step 1 : Configuration ---%s\n\n" "${yellow}" "${reset}"

# In CI mode, env file is mandatory
if $CI_MODE; then
  if [[ -z "$ENV_FILE" ]]; then
    print_box "❌ Error : in CI mode, -e|--env is required" "${red}"
    exit 1
  fi

  if [[ ! -f "$ENV_FILE" ]]; then
    print_box "❌ Error : env file $ENV_FILE not found" "${red}"
    exit 1
  fi

  printf "%s❗ CI mode, skipping configuration prompts%s\n\n" "${blue}" "${reset}"
else
  printf "%sℹ️ Tip : Press Enter to accept default values%s\n\n" "${magenta}" "${reset}"
  # ask directory
  if [ ! "$ARG_DIR" = true ] ; then
    dir_choice=$(prompt_input '1/4 Install directory ("current" or "home")' "home")

    case "$dir_choice" in
    current) DIR=$(realpath ".") ;;
    home) DIR=$(realpath "~") ;;
    *)
      print_box "❌ Error : invalid choice [ $dir_choice ]" "${red}"
      exit 1
      ;;
    esac
  fi

  # ask folder name
  if [ ! "$ARG_FOLDER" = true ] ; then
    FOLDER=$(prompt_input "2/4 Folder name to clone into" "$FOLDER")
  fi

  # ask env file path
  if [ ! "$ARG_ENV" = true ] ; then
    ENV_FILE=$(prompt_input "3/4 Path to env file containing pre-filled values (optional)" "" true)
  fi

  # ask git url
  if [ ! "$ARG_GIT" = true ] ; then
    GIT_URL=$(prompt_input "4/4 Git repository URL (must match the following format)" "$GIT_URL")
  fi
fi

if [[ -n "$ENV_FILE" && ! "$ENV_FILE" =~ ^/ ]]; then
  ENV_FILE="$WORKING_DIR/$ENV_FILE"
fi

# 2) Clone repo into named folder
TARGET="${DIR%/}/$FOLDER"
printf "\n%s--- 📋 Step 2 : Cloning repository into %s... ---%s\n\n" "${yellow}" "$TARGET" "${reset}"
parent_dir=$(dirname "$TARGET")

# Check write permission on parent directory
if [[ ! -w "$parent_dir" ]]; then
  print_box "❌ Error : no write permission to $parent_dir" "${red}"
  exit 1
fi

# Check if target directory already exists
if [[ -d "$TARGET" ]]; then
  printf "%s❗ Directory %s already exists%s\n" "${magenta}" "$TARGET" "${reset}"
  printf "%s❓ Do you want to remove it ?%s\n" "${blue}" "${reset}"
  printf "%s⚠️ Warning : this will delete all files in the directory%s\n" "${red}" "${reset}"
  if prompt_confirm; then
    rm -fr "$TARGET" || {
      print_box "❌ Error : failed to remove directory" "${red}"
      exit 1
    }
    printf "%s✅ Directory removed%s\n\n" "${green}" "${reset}"
  else
    print_box "❌ Error : setup aborted" "${red}"
    exit 1
  fi
fi

git clone --quiet "$GIT_URL" "$TARGET" || {
  print_box "❌ Error : failed to clone repository" "${red}"
  exit 1
}
printf "%s✅ Repository cloned%s\n\n" "${green}" "${reset}"
cd "$TARGET"

# 3) Prepare .env
printf "\n%s--- 📝 Step 3 : Preparing .env file ---%s\n\n" "${yellow}" "${reset}"
# variable definitions and regex patterns
vars=(APP_ID API_HASH BOT_OWNER BOT_TOKEN MONGODB_DBNAME MONGODB_URL LOGS_CHANNEL)

declare -A regexes=(
  [APP_ID]='^[0-9]+$'
  [API_HASH]='^[A-Fa-f0-9]+$'
  [BOT_OWNER]='^[0-9]+$'
  [BOT_TOKEN]='^[0-9]+:[A-Za-z0-9_-]+$'
  [MONGODB_DBNAME]='^[A-Za-z0-9._-]+$'
  [MONGODB_URL]='^.+://.+$'
  [LOGS_CHANNEL]='^-?[0-9]+$'
)

if [[ -z "$ENV_FILE" ]]; then
  ENV_FILE="${TARGET}/.env"
fi

if $CI_MODE; then
  # load and validate from ENV_FILE
  for name in "${vars[@]}"; do
    val=$(grep -E "^$name=" "$ENV_FILE" |
      cut -d= -f2- |
      tr -d $'\r')
    [[ -n "$val" ]] || {
      print_box "❌ Error : $name missing in $ENV_FILE" "${red}"
      exit 1
    }
    validate_var "$name" "$val" "${regexes[$name]}"
    echo "$name=$val" >>.env
  done
else
  # interactive prompts
  # read existing .env defaults if present
  declare -A defaults

  if [[ -f $ENV_FILE ]]; then
    while IFS= read -r line; do
      line="${line//$'\r'/}"
      line="${line#"${line%%[![:space:]]*}"}"
      line="${line%"${line##*[![:space:]]}"}"
      key="${line%%=*}"
      val="${line#*=}"

      for want in "${vars[@]}"; do
        if [[ "$key" == "$want" ]]; then
          defaults[$key]="$val"
          break
        fi
      done
    done <"$ENV_FILE"

    printf "%sℹ️ Tip : Press Enter to accept default values%s\n\n" "${magenta}" "${reset}"
  fi

  for name in "${vars[@]}"; do
    default="${defaults[$name]:-}"
    prompt="Enter $name"
    val=$(prompt_input "$prompt" "$default")
    validate_var "$name" "$val" "${regexes[$name]}"
    echo "$name=$val" >>.env
  done
fi

printf "\n%s✅ .env file filled%s\n\n" "${green}" "${reset}"

# 4) Build Docker image
printf "\n%s--- 🛠️ Step 4 : Building Docker image ---%s\n\n" "${yellow}" "${reset}"
docker build -t edm115/unzip-bot .

# 5) Run Docker container
printf "\n%s--- 🚀 Step 5 : Starting Docker container ---%s\n\n" "${yellow}" "${reset}"
docker run -d \
  -v downloaded-volume-prod:/app/Downloaded \
  -v thumbnails-volume-prod:/app/Thumbnails \
  --env-file ./.env \
  --name unzipbot edm115/unzip-bot
print_box $'✅ Setup complete\nThe bot is running, check Telegram !' "${green}"
info=$(docker inspect -f $'ℹ️ Docker info\n\nID : {{.Id}}\nName : {{.Name}}\nStatus : {{.State.Status}}\nImage : {{.Config.Image}}\nCreated at : {{.Created}}' unzipbot)
print_box "$info" "${blue}"
