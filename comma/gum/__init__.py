# [flavio@flavios-air ~/projects/,][main]
# $ gum --help
# Usage: gum <command>
# A tool for glamorous shell scripts.
# Flags:
#   -h, --help       Show context-sensitive help.
#   -v, --version    Print the version number
# Commands:
#   choose     Choose an option from a list of choices
#   confirm    Ask a user to confirm an action
#   file       Pick a file from a folder
#   filter     Filter items from a list
#   format     Format a string using a template
#   input      Prompt for some input
#   join       Join text vertically or horizontally
#   pager      Scroll through a file
#   spin       Display spinner while running a command
#   style      Apply coloring, borders, spacing to text
#   table      Render a table of data
#   write      Prompt for long-form text
# Run "gum <command> --help" for more information on a command.
# gum choose --help
# Usage: gum choose [<options> ...]
# Choose an option from a list of choices
# Arguments:
#   [<options> ...]    Options to choose from.
# Flags:
#   -h, --help                      Show context-sensitive help.
#   -v, --version                   Print the version number
#       --ordered                   Maintain the order of the selected options
#                                   ($GUM_CHOOSE_ORDERED)
#       --height=10                 Height of the list ($GUM_CHOOSE_HEIGHT)
#       --cursor="> "               Prefix to show on item that corresponds to the
#                                   cursor position ($GUM_CHOOSE_CURSOR)
#       --header=""                 Header value ($GUM_CHOOSE_HEADER)
#       --cursor-prefix="○ "        Prefix to show on the cursor item (hidden if
#                                   limit is 1) ($GUM_CHOOSE_CURSOR_PREFIX)
#       --selected-prefix="◉ "      Prefix to show on selected items (hidden if
#                                   limit is 1) ($GUM_CHOOSE_SELECTED_PREFIX)
#       --unselected-prefix="○ "
#                                   Prefix to show on unselected items (hidden if
#                                   limit is 1) ($GUM_CHOOSE_UNSELECTED_PREFIX)
#       --selected=,...             Options that should start as selected
#                                   ($GUM_CHOOSE_SELECTED)
#       --timeout=0                 Timeout until choose returns selected element
#                                   ($GUM_CCHOOSE_TIMEOUT)
# Selection
#   --limit=1     Maximum number of options to pick
#   --no-limit    Pick unlimited number of options (ignores limit)
# Style Flags
#   --cursor.foreground="212"      Foreground Color
#                                  ($GUM_CHOOSE_CURSOR_FOREGROUND)
#   --header.foreground="240"      Foreground Color
#                                  ($GUM_CHOOSE_HEADER_FOREGROUND)
#   --item.foreground=""           Foreground Color ($GUM_CHOOSE_ITEM_FOREGROUND)
#   --selected.foreground="212"    Foreground Color
#                                  ($GUM_CHOOSE_SELECTED_FOREGROUND)
# gum confirm --help
# Usage: gum confirm [<prompt>]
# Ask a user to confirm an action
# Arguments:
#   [<prompt>]    Prompt to display.
# Flags:
#   -h, --help                 Show context-sensitive help.
#   -v, --version              Print the version number
#       --default              Default confirmation action
#       --affirmative="Yes"    The title of the affirmative action
#       --negative="No"        The title of the negative action
#       --timeout=0            Timeout until confirm returns selected value or
#                              default if provided ($GUM_CONFIRM_TIMEOUT)
# Style Flags
#   --prompt.foreground=""           Foreground Color
#                                    ($GUM_CONFIRM_PROMPT_FOREGROUND)
#   --selected.foreground="230"      Foreground Color
#                                    ($GUM_CONFIRM_SELECTED_FOREGROUND)
#   --unselected.foreground="254"    Foreground Color
#                                    ($GUM_CONFIRM_UNSELECTED_FOREGROUND)
# gum file --help
# Usage: gum file [<path>]
# Pick a file from a folder
# Arguments:
#   [<path>]    The path to the folder to begin traversing ($GUM_FILE_PATH)
# Flags:
#   -h, --help          Show context-sensitive help.
#   -v, --version       Print the version number
#   -c, --cursor=">"    The cursor character ($GUM_FILE_CURSOR)
#   -a, --all           Show hidden and 'dot' files ($GUM_FILE_ALL)
#       --file          Allow files selection ($GUM_FILE_FILE)
#       --directory     Allow directories selection ($GUM_FILE_DIRECTORY)
#       --height=0      Maximum number of files to display ($GUM_FILE_HEIGHT)
#       --timeout=0     Timeout until command aborts without a selection
#                       ($GUM_FILE_TIMEOUT)
# Style Flags
#   --cursor.foreground="212"       Foreground Color ($GUM_FILE_CURSOR_FOREGROUND)
#   --symlink.foreground="36"       Foreground Color
#                                   ($GUM_FILE_SYMLINK_FOREGROUND)
#   --directory.foreground="99"     Foreground Color
#                                   ($GUM_FILE_DIRECTORY_FOREGROUND)
#   --file.foreground=""            Foreground Color ($GUM_FILE_FILE_FOREGROUND)
#   --permissions.foreground="244"
#                                   Foreground Color
#                                   ($GUM_FILE_PERMISSIONS_FOREGROUND)
#   --selected.foreground="212"     Foreground Color
#                                   ($GUM_FILE_SELECTED_FOREGROUND)
#   --file-size.foreground="240"    Foreground Color
#                                   ($GUM_FILE_FILE_SIZE_FOREGROUND)
# gum filter --help
# Usage: gum filter
# Filter items from a list
# Flags:
#   -h, --help                       Show context-sensitive help.
#   -v, --version                    Print the version number
#       --indicator="•"              Character for selection
#                                    ($GUM_FILTER_INDICATOR)
#       --selected-prefix=" ◉ "      Character to indicate selected items (hidden
#                                    if limit is 1) ($GUM_FILTER_SELECTED_PREFIX)
#       --unselected-prefix=" ○ "
#                                    Character to indicate unselected
#                                    items (hidden if limit is 1)
#                                    ($GUM_FILTER_UNSELECTED_PREFIX)
#       --header=""                  Header value ($GUM_FILTER_HEADER)
#       --placeholder="Filter..."    Placeholder value ($GUM_FILTER_PLACEHOLDER)
#       --prompt="> "                Prompt to display ($GUM_FILTER_PROMPT)
#       --width=20                   Input width ($GUM_FILTER_WIDTH)
#       --height=0                   Input height ($GUM_FILTER_HEIGHT)
#       --value=""                   Initial filter value ($GUM_FILTER_VALUE)
#       --reverse                    Display from the bottom of the screen
#                                    ($GUM_FILTER_REVERSE)
#       --[no-]fuzzy                 Enable fuzzy matching ($GUM_FILTER_FUZZY)
#       --[no-]sort                  Sort the results ($GUM_FILTER_SORT)
#       --timeout=0                  Timeout until filter command aborts
#                                    ($GUM_FILTER_TIMEOUT)
# Style Flags
#   --indicator.foreground="212"    Foreground Color
#                                   ($GUM_FILTER_INDICATOR_FOREGROUND)
#   --selected-indicator.foreground="212"
#                                   Foreground Color
#                                   ($GUM_FILTER_SELECTED_PREFIX_FOREGROUND)
#   --unselected-prefix.foreground="240"
#                                   Foreground Color
#                                   ($GUM_FILTER_UNSELECTED_PREFIX_FOREGROUND)
#   --header.foreground="240"       Foreground Color
#                                   ($GUM_FILTER_HEADER_FOREGROUND)
#   --text.foreground=""            Foreground Color ($GUM_FILTER_TEXT_FOREGROUND)
#   --cursor-text.foreground=""     Foreground Color
#                                   ($GUM_FILTER_CURSOR_TEXT_FOREGROUND)
#   --match.foreground="212"        Foreground Color
#                                   ($GUM_FILTER_MATCH_FOREGROUND)
#   --prompt.foreground="240"       Foreground Color
#                                   ($GUM_FILTER_PROMPT_FOREGROUND)
# Selection
#   --limit=1        Maximum number of options to pick
#   --no-limit       Pick unlimited number of options (ignores limit)
#   --[no-]strict    Only returns if anything matched. Otherwise return Filter
# gum format --help
# Usage: gum format [<template> ...]
# Format a string using a template
# Arguments:
#   [<template> ...]    Template string to format (can also be provided via stdin)
# Flags:
#   -h, --help               Show context-sensitive help.
#   -v, --version            Print the version number
#       --theme="pink"       Glamour theme to use for markdown formatting
#                            ($GUM_FORMAT_THEME)
#   -l, --language=""        Programming language to parse code
#                            ($GUM_FORMAT_LANGUAGE)
#   -t, --type="markdown"    Format to use (markdown,template,code,emoji)
#                            ($GUM_FORMAT_TYPE)
# gum input --help
# Usage: gum input
# Prompt for some input
# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number
#       --placeholder="Type something..."
#                                Placeholder value ($GUM_INPUT_PLACEHOLDER)
#       --prompt="> "            Prompt to display ($GUM_INPUT_PROMPT)
#       --cursor.mode="blink"    Cursor mode ($GUM_INPUT_CURSOR_MODE)
#       --value=""               Initial value (can also be passed via stdin)
#       --char-limit=400         Maximum value length (0 for no limit)
#       --width=40               Input width (0 for terminal width)
#                                ($GUM_INPUT_WIDTH)
#       --password               Mask input characters
#       --header=""              Header value ($GUM_INPUT_HEADER)
#       --timeout=0              Timeout until input aborts ($GUM_INPUT_TIMEOUT)
# Style Flags
#   --prompt.foreground=""       Foreground Color ($GUM_INPUT_PROMPT_FOREGROUND)
#   --cursor.foreground="212"    Foreground Color ($GUM_INPUT_CURSOR_FOREGROUND)
#   --header.foreground="240"    Foreground Color ($GUM_INPUT_HEADER_FOREGROUND)
# gum join --help
# Usage: gum join <text> ...
# Join text vertically or horizontally
# Arguments:
#   <text> ...    Text to join.
# Flags:
#   -h, --help            Show context-sensitive help.
#   -v, --version         Print the version number
#       --align="left"    Text alignment
#       --horizontal      Join (potentially multi-line) strings horizontally
#       --vertical        Join (potentially multi-line) strings vertically
# gum pager --help
# Usage: gum pager [<content>]
# Scroll through a file
# Arguments:
#   [<content>]    Display content to scroll
# Flags:
#   -h, --help                 Show context-sensitive help.
#   -v, --version              Print the version number
#       --show-line-numbers    Show line numbers
#       --soft-wrap            Soft wrap lines
#       --timeout=0            Timeout until command exits ($GUM_PAGER_TIMEOUT)
# Style Flags
#   --help.foreground="241"     Foreground Color ($GUM_PAGER_HELP_FOREGROUND)
#   --line-number.foreground="237"
#                               Foreground Color
#                               ($GUM_PAGER_LINE_NUMBER_FOREGROUND)
#   --match.foreground="212"    Foreground Color ($GUM_PAGER_MATCH_FOREGROUND)
#   --match-highlight.foreground="235"
#                               Foreground Color
#                               ($GUM_PAGER_MATCH_HIGH_FOREGROUND)
# gum spin --help
# Usage: gum spin <command> ...
# Display spinner while running a command
# Arguments:
#   <command> ...    Command to run
# Flags:
#   -h, --help                  Show context-sensitive help.
#   -v, --version               Print the version number
#       --show-output           Show or pipe output of command during execution
#                               ($GUM_SPIN_SHOW_OUTPUT)
#   -s, --spinner="dot"         Spinner type ($GUM_SPIN_SPINNER)
#       --title="Loading..."    Text to display to user while spinning
#                               ($GUM_SPIN_TITLE)
#   -a, --align="left"          Alignment of spinner with regard to the title
#                               ($GUM_SPIN_ALIGN)
#       --timeout=0             Timeout until spin command aborts
#                               ($GUM_SPIN_TIMEOUT)
# Style Flags
#   --spinner.foreground="212"    Foreground Color ($GUM_SPIN_SPINNER_FOREGROUND)
#   --title.foreground=""         Foreground Color ($GUM_SPIN_TITLE_FOREGROUND)
# gum style --help
# Usage: gum style [<text> ...]
# Apply coloring, borders, spacing to text
# Arguments:
#   [<text> ...]    Text to which to apply the style
# Flags:
#   -h, --help       Show context-sensitive help.
#   -v, --version    Print the version number
# Style Flags
#   --background=""           Background Color ($BACKGROUND)
#   --foreground=""           Foreground Color ($FOREGROUND)
#   --border="none"           Border Style ($BORDER)
#   --border-background=""    Border Background Color ($BORDER_BACKGROUND)
#   --border-foreground=""    Border Foreground Color ($BORDER_FOREGROUND)
#   --align="left"            Text Alignment ($ALIGN)
#   --height=0                Text height ($HEIGHT)
#   --width=0                 Text width ($WIDTH)
#   --margin="0 0"            Text margin ($MARGIN)
#   --padding="0 0"           Text padding ($PADDING)
#   --bold                    Bold text ($BOLD)
#   --faint                   Faint text ($FAINT)
#   --italic                  Italicize text ($ITALIC)
#   --strikethrough           Strikethrough text ($STRIKETHROUGH)
#   --underline               Underline text ($UNDERLINE)
# gum table --help
# Usage: gum table
# Render a table of data
# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number
#   -s, --separator=","          Row separator
#   -c, --columns=COLUMNS,...    Column names
#   -w, --widths=WIDTHS,...      Column widths
#       --height=10              Table height
#   -f, --file=""                file path
# Style Flags
#   --cell.foreground=""           Foreground Color ($GUM_TABLE_CELL_FOREGROUND)
#   --header.foreground=""         Foreground Color ($GUM_TABLE_HEADER_FOREGROUND)
#   --selected.foreground="212"    Foreground Color
#                                  ($GUM_TABLE_SELECTED_FOREGROUND)
# gum write --help
# Usage: gum write
# Prompt for long-form text
# Flags:
#   -h, --help                   Show context-sensitive help.
#   -v, --version                Print the version number
#       --width=50               Text area width (0 for terminal width)
#                                ($GUM_WRITE_WIDTH)
#       --height=5               Text area height ($GUM_WRITE_HEIGHT)
#       --header=""              Header value ($GUM_WRITE_HEADER)
#       --placeholder="Write something..."
#                                Placeholder value ($GUM_WRITE_PLACEHOLDER)
#       --prompt="┃ "            Prompt to display ($GUM_WRITE_PROMPT)
#       --show-cursor-line       Show cursor line ($GUM_WRITE_SHOW_CURSOR_LINE)
#       --show-line-numbers      Show line numbers ($GUM_WRITE_SHOW_LINE_NUMBERS)
#       --value=""               Initial value (can be passed via stdin)
#                                ($GUM_WRITE_VALUE)
#       --char-limit=400         Maximum value length (0 for no limit)
#       --cursor.mode="blink"    Cursor mode ($GUM_WRITE_CURSOR_MODE)
# Style Flags
#   --base.foreground=""            Foreground Color ($GUM_WRITE_BASE_FOREGROUND)
#   --cursor-line-number.foreground="7"
#                                   Foreground Color
#                                   ($GUM_WRITE_CURSOR_LINE_NUMBER_FOREGROUND)
#   --cursor-line.foreground=""     Foreground Color
#                                   ($GUM_WRITE_CURSOR_LINE_FOREGROUND)
#   --cursor.foreground="212"       Foreground Color
#                                   ($GUM_WRITE_CURSOR_FOREGROUND)
#   --end-of-buffer.foreground="0"
#                                   Foreground Color
#                                   ($GUM_WRITE_END_OF_BUFFER_FOREGROUND)
#   --line-number.foreground="7"    Foreground Color
#                                   ($GUM_WRITE_LINE_NUMBER_FOREGROUND)
#   --header.foreground="240"       Foreground Color
#                                   ($GUM_WRITE_HEADER_FOREGROUND)
#   --placeholder.foreground="240"
#                                   Foreground Color
#                                   ($GUM_WRITE_PLACEHOLDER_FOREGROUND)
#   --prompt.foreground="7"         Foreground Color
#                                   ($GUM_WRITE_PROMPT_FOREGROUND)
from __future__ import annotations
