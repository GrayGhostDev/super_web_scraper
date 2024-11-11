from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}."
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response."
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

def parse_with_ollama(dom_chunks, parse_description, model_name="llama2:3.2", temperature=0.7, max_tokens=500):
    """Parse content chunks using the LLM."""
    try:
        prompt = ChatPromptTemplate.from_template(template)
        model = OllamaLLM(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30  # Add timeout to prevent hanging
        )
        chain = prompt | model

        parsed_results = []
        total_chunks = len(dom_chunks)

        for i, chunk in enumerate(dom_chunks, start=1):
            try:
                logger.info(f"Parsing chunk {i} of {total_chunks}")
                response = chain.invoke({
                    "dom_content": chunk,
                    "parse_description": parse_description
                })
                parsed_results.append(response)
                logger.info(f"Successfully parsed chunk {i}")
            except Exception as e:
                logger.error(f"Error parsing chunk {i}: {str(e)}")
                parsed_results.append("")

        return "\n".join(filter(None, parsed_results))
    except Exception as e:
        logger.error(f"Fatal error in parse_with_ollama: {str(e)}")
        raise Exception(f"Failed to initialize parsing: {str(e)}")