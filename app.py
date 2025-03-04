import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import os

# Removed dotenv since the key will be provided by the user

system_prompt = """\
You are an expert assistant that creates LLMs.txt files for websites. 
The user will provide information about their site: name, overview, key pages, 
and any extra notes or links. 

Your job is to return two separate pieces of Markdown text in **JSON** format:

1) "llms_txt": A short, basic LLMs.txt version (like a site map for AI). 
2) "llms_full_txt": A more comprehensive version (llms-full.txt) that provides 
   detailed information, including extended documentation, code snippets, etc.

Return them as a valid JSON object with exactly two keys: "llms_txt" and "llms_full_txt".

Example JSON output:
{
  "llms_txt": "...(short text in Markdown)...",
  "llms_full_txt": "...(detailed text in Markdown)..."
}

Make sure these are valid Markdown strings. 
Do not include any additional keys.
"""

user_prompt_template = """
Please create two files, llms.txt and llms-full.txt, in Markdown based on the following website information:

Website Name: {website_name}
Overview: {overview}
Key Pages: {key_pages}
Additional Notes: {notes}

Remember:
- "llms.txt" is a brief overview, covering site structure and main pages.
- "llms-full.txt" is a more comprehensive version with extended details. 
- Return both in JSON: with keys "llms_txt" and "llms_full_txt".
"""

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", user_prompt_template),
    ]
)

def main():
    st.title("LLMs.txt Generator (LLMO Project)")
    st.write("Fill out the information below to generate your `llms.txt` and `llms-full.txt`.")
    

    openai_key = st.text_input("Enter your OpenAI API Key", type="password")
    
    website_name = st.text_input("Website Name/Title", "Example.com")
    overview = st.text_area("Overview", "This is a site about AI and web development.")
    key_pages = st.text_area(
        "Key Topics/Pages (use line breaks or bullet points)",
        "- Home\n- Blog\n- Products\n- Contact\n- Tutorials"
    )
    notes = st.text_area("Additional Notes", "We offer extensive AI tutorials and an API reference.")
    
    if st.button("Generate Files"):
        if not openai_key:
            st.error("Please enter your OpenAI API Key.")
            return
        
        
        os.environ["OPENAI_API_KEY"] = openai_key
        
        prompt_args = {
            "website_name": str(website_name),
            "overview": str(overview),
            "key_pages": str(key_pages),
            "notes": str(notes)
        }
        
        # Initialize the LLM with the provided API key
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_key
        )
        
        model_chain = prompt_template | llm
        response = model_chain.invoke(prompt_args)
        
        try:
            data = json.loads(response.content.strip())
            llms_txt_content = data["llms_txt"]
            llms_full_txt_content = data["llms_full_txt"]
        except Exception as e:
            st.error(f"Failed to parse JSON. Error: {str(e)}")
            return
        
        st.session_state.llms_txt_content = llms_txt_content
        st.session_state.llms_full_txt_content = llms_full_txt_content

    if "llms_txt_content" in st.session_state and "llms_full_txt_content" in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("llms.txt (Short Version)")
            st.code(st.session_state.llms_txt_content, language="markdown")
            llms_txt_bytes = st.session_state.llms_txt_content.encode("utf-8")
            st.download_button(
                label="Download llms.txt",
                data=llms_txt_bytes,
                file_name="llms.txt",
                mime="text/markdown"
            )
        
        with col2:
            st.subheader("llms-full.txt (Detailed)")
            st.code(st.session_state.llms_full_txt_content, language="markdown")
            llms_full_txt_bytes = st.session_state.llms_full_txt_content.encode("utf-8")
            st.download_button(
                label="Download llms-full.txt",
                data=llms_full_txt_bytes,
                file_name="llms-full.txt",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()
