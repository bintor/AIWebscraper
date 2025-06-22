import streamlit as st
from scrape import (scrape_website, split_dom_content, clean_body_content, extract_body_content)
from parse import parse_with_ollama
from export import export_to_csv, export_to_json, export_raw_text, structure_parsed_data

st.title("Web Scraper Brian")
url = st.text_input("Enter a Website URL:")

if st.button("Scrape Site"):
    with st.spinner("Scraping the website..."):
        dom_content = scrape_website(url)
        body_content = extract_body_content(dom_content)
        cleaned_content = clean_body_content(body_content)

        st.session_state.dom_content = cleaned_content
        st.session_state.raw_html = dom_content
        
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)
        
        st.success("Scraping completed!")

# Add export raw content functionality after scraping
if "dom_content" in st.session_state:
    st.subheader("Raw Content")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        raw_export_format = st.radio(
            "Raw Export Format",
            ["Text", "JSON", "CSV"],
            index=0,
            key="raw_export_format"
        )
    
    with col2:
        raw_custom_filename = st.text_input("Filename for raw content (optional)", key="raw_filename")
    
    with col3:
        export_button_label = f"Export Raw as {raw_export_format}"
        if st.button(export_button_label):
            with st.spinner(f"Exporting raw content as {raw_export_format}..."):
                if raw_export_format == "Text":
                    # Export as plain text
                    file_path = export_raw_text(
                        st.session_state.dom_content, 
                        raw_custom_filename
                    )
                    st.success(f"Exported raw content to {file_path}")
                
                elif raw_export_format == "JSON":
                    # For JSON, create a simple dictionary with the content
                    raw_data = {
                        "url": url,
                        "timestamp": str(st.session_state.get("scrape_time", "")),
                        "content": st.session_state.dom_content
                    }
                    file_path = export_to_json(raw_data, raw_custom_filename)
                    st.success(f"Exported raw content to {file_path}")
                
                elif raw_export_format == "CSV":
                    # For CSV, create rows from the content
                    # Split by lines and create a data structure that works in CSV
                    lines = st.session_state.dom_content.split('\n')
                    raw_data = [{"line_number": i+1, "content": line} for i, line in enumerate(lines) if line.strip()]
                    file_path = export_to_csv(raw_data, raw_custom_filename)
                    st.success(f"Exported raw content to {file_path}")
    
    st.divider()  # Add a visual divider between raw export and parsing

# Parsing section
if "dom_content" in st.session_state:
    st.subheader("Parse Content")
    parse_description = st.text_area("Describe what you want to parse")

    col1, col2 = st.columns(2)
    with col1:
        output_format = st.radio(
            "Output Format",
            ["Text", "JSON", "CSV"],
            index=0,
            key="parse_output_format"
        )
    
    with col2:
        if output_format in ["JSON", "CSV"]:
            custom_filename = st.text_input("Custom filename (optional)", key="parse_filename")

    if st.button("Parse Content"):
        if parse_description:
            with st.spinner("Parsing the content..."):
                dom_chunks = split_dom_content(st.session_state.dom_content)

                # Pass the output format to the parse function
                parsed_result = parse_with_ollama(
                    dom_chunks, 
                    parse_description,
                    output_format.lower()
                )

                # Display the parsed result
                st.subheader("Parsed Result")
                st.text_area("Result", parsed_result, height=300)
                
                # Store the parsed result in session state
                st.session_state.parsed_result = parsed_result
                
                # Export functionality
                if output_format in ["JSON", "CSV"]:
                    st.subheader("Export Data")

                    # Attempt to structure the data
                    structured_data = structure_parsed_data(parsed_result)
                    
                    # Store structured data in session state for export buttons
                    st.session_state.structured_data = structured_data
                    st.session_state.custom_filename = custom_filename if 'custom_filename' in locals() else None

                    # Show a preview of structured data
                    st.json(structured_data)

# Create separate export buttons outside the if st.button("Parse Content") block
# to avoid nested button issues
if "parsed_result" in st.session_state and "structured_data" in st.session_state:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as JSON", key="export_json"):
            with st.spinner("Exporting to JSON..."):
                filename = st.session_state.get("custom_filename")
                file_path = export_to_json(st.session_state.structured_data, filename)
                st.success(f"Exported to {file_path}")
    
    with col2:
        if st.button("Export as CSV", key="export_csv"):
            with st.spinner("Exporting to CSV..."):
                filename = st.session_state.get("custom_filename")
                file_path = export_to_csv(st.session_state.structured_data, filename)
                st.success(f"Exported to {file_path}")

# Download button for raw HTML
if "raw_html" in st.session_state:
    st.download_button(
        label="Download Raw HTML",
        data=st.session_state.raw_html,
        file_name="raw_webpage.html",
        mime="text/html"
    )