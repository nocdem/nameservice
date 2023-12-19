#!/bin/bash

group="global.gns"
cellframe_node_cli_path="/opt/cellframe-node/bin/cellframe-node-cli"
expected_address_length=104

# Function to print wallet address information
print_wallet_info() {
    local key="$1"
    local regdate="$2"
    local valuecell="$3"
    local valuekel="$4"

    echo "Content-type: text/html"
    echo ""
    echo "<html>"
    echo "<head>"
    echo "<title>Search Results</title>"
    echo "</head>"
    echo "<body>"
    echo "<h1>Search Results:</h1>"
    echo "<hr>"
    echo "<p><strong>Alias:</strong> $key</p>"
    echo "<p><strong>Registration date:</strong> $regdate</p>"

    addresscell=$(echo "$valuecell" | tail -c 106 | tr -cd '[:alnum:]')
    addresskel=$(echo "$valuekel" | tail -c 106 | tr -cd '[:alnum:]')

    if [ ${#addresscell} -eq 104 ]; then
        echo "<p><strong>Cellframe Wallet Address:</strong> $addresscell</p>"
    else
        echo "<p style='color: red;'><strong>Invalid Cellframe Wallet Address:</strong> $addresscell (Length: ${#addresscell})</p>"
    fi

    if [ ${#addresskel} -eq 104 ]; then
        echo "<p><strong>KelVPN Wallet Address:</strong> $addresskel</p>"
    else
        echo "<p style='color: red;'><strong>Invalid KelVPN Wallet Address:</strong> $addresskel (Length: ${#addresskel})</p>"
    fi

    echo "<hr>"
    echo "</body>"
    echo "</html>"
}

# Function to perform the search
search_and_display() {
    local search_term="$1"
    local is_reverse_search="$2"
    local found=false  # Flag to check if anything is found

    keys=$("$cellframe_node_cli_path" global_db get_keys -group "$group" | grep -E "^[^.]+$" | head -n -1)

    while IFS= read -r key; do
        if [ -z "$key" ]; then
            continue
        fi

        value=$("$cellframe_node_cli_path" global_db read -group "$group" -key "$key")
        regdate=$(echo "$value" | awk '/data:/ {getline; gsub(/^[ \t]+|[ \t]+$/, ""); print}')

        valuecell=$("$cellframe_node_cli_path" global_db read -group "$group" -key "$key.cell")
        valuekel=$("$cellframe_node_cli_path" global_db read -group "$group" -key "$key.kel")

        # Perform the search based on the selected option
        if [ "$is_reverse_search" = false ]; then
            if [ "$key" == "$search_term" ]; then
                found=true  # Set the flag to true if found in normal search

                print_wallet_info "$key" "$regdate" "$valuecell" "$valuekel"
echo "found $found"
            fi
        else
            if [[ "$valuekel" == *"$search_term"* ]] || [[ "$valuecell" == *"$search_term"* ]]; then
            if [ "$found" = false ]; then
echo "found $found"

                print_wallet_info "$key" "$regdate" "$valuecell" "$valuekel"
fi
            fi
        fi

    done <<< "$keys"

    # If anything is found in normal search, skip reverse search
    if [ "$found" = true ]; then
        return
    fi

    # If no results found, display the "Not Found" form
if [ "$found" = false ]; then

    echo "Content-type: text/html"
    echo ""
    echo "<html>"
    echo "<head>"
    echo "<title>Not Found</title>"
    echo "</head>"
    echo "<body>"
    echo "<h1>No results found for '$search_term'</h1>"
    echo "<p><a href='$SCRIPT_NAME'>Back to Search</a></p>"
    echo "</body>"
    echo "</html>"
fi
}

# Display HTML form for search
display_search_form() {
    echo "Content-type: text/html"
    echo ""
    echo "<html>"
    echo "<head>"
    echo "<title>Search</title>"
    echo "</head>"
    echo "<body>"
    echo "<h1>Search</h1>"
    echo "<form action='$SCRIPT_NAME' method='GET'>"
    echo "<label for='search_term'>Enter alias or wallet addr:</label>"
    echo "<input type='text' id='search_term' name='search_term'>"
    echo "<input type='submit' value='Search'>"
    echo "</form>"
    echo "</body>"
    echo "</html>"
}

# Get the search term from the CGI query string
query_string="$QUERY_STRING"
search_term=$(echo "$query_string" | awk -F'&' '{print $1}' | awk -F'=' '{print $2}')

# If there is a search term, perform both normal and reverse searches and display the results
if [ -n "$search_term" ]; then
    search_and_display "$search_term" false  # Normal search
    search_and_display "$search_term" true   # Reverse search
else
    # Otherwise, display the search form
    display_search_form
fi
