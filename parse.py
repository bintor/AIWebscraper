from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def parse_with_ollama(dom_chunks, parse_description, output_format="text"):
    """
    Parse DOM content chunks using LangChain and Ollama.

    Args:
        dom_chunks : List of text chunks from the DOM
        parse_description: Description of what to parse
        output_format: Desired output format ("text", "json", "csv")

    Returns:
        parsed_results: The result of the parsing
    """
    # Adjust the prompt based on the desired output format
    format_instruction = ""
    if output_format.lower() == "json":
        format_instruction = "Format your output as valid JSON data."
    elif output_format.lower() == "csv":
        format_instruction = "Format your output with clear key-value pairs that can be converted to CSV"

    # Create the prompt template
    template = (
        "You are tasked with extracting specific information from the following text content: {dom_content}. "
        "Please follow these instructions carefully: \n\n"
        "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
        "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
        "3. **Empty Response:** If no information matches the description, return an empty string ('')."
        "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
        f"5. {format_instruction}"
    )

    # Initialize the LLM and chain
    model = OllamaLLM(model="llama3")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []

    # Process each chunk
    try:
        for i, chunk in enumerate(dom_chunks, start=1):
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            print(f"Parsed batch: {i} of {len(dom_chunks)}")
            parsed_results.append(response)
    except Exception as e:
        print(f"Error parsing content: {str(e)}")
        return f"Error: {str(e)}"
    
    # If we have multiple chunks, consolidate the results
    if len(parsed_results) > 1:
        combined_result = consolidate_outputs(parsed_results, parse_description, output_format)
        return combined_result
    elif len(parsed_results) == 1:
        return parsed_results[0]
    else:
        return ""

def consolidate_outputs(outputs, parse_description, output_format="text"):
    """
    Consolidate outputs from multiple chunks into a single coherent result.

    Args:
        outputs: List of parsing results from each chunk
        parse_description: Original parsing request
        output_format: Desired output format

    Returns:
        consolidated_result: Combined and deduplicated result
    """
    # For a single output, just return it
    if len(outputs) == 1:
        return outputs[0]

    # For simple consolidation, join with newlines
    if all(not output.strip() for output in outputs):
        return ""
    
    # For more complex consolidation, use the LLM again
    consolidation_template = (
        "You are tasked with consolidating multiple parsing results into a single coherent output. "
        "The original parsing request was: {parse_description}\n\n"
        "Here are the individual results from different chunks:\n{combined_outputs}\n\n"
        "Please consolidate these results by:\n"
        "1. Removing any duplicates\n"
        "2. Organizing the information logically\n"
        "3. Ensuring the output is formatted appropriately"
    )
    
    if output_format.lower() == "json":
        consolidation_template += "\n4. Ensuring the final output is valid JSON"
    elif output_format.lower() == "csv":
        consolidation_template += "\n4. Ensuring the final output has clear key-value pairs for CSV conversion"
    
    model = OllamaLLM(model="llama3")
    prompt = ChatPromptTemplate.from_template(consolidation_template)
    chain = prompt | model
    
    try:
        combined_outputs = "\n\n---\n\n".join(outputs)
        consolidated_result = chain.invoke(
            {"parse_description": parse_description, "combined_outputs": combined_outputs}
        )
        return consolidated_result
    except Exception as e:
        print(f"Error consolidating outputs: {str(e)}")
        # Fall back to simple joining if consolidation fails
        return "\n\n".join(outputs)
   