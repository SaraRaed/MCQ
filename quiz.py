import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import re
import os

os.environ['OPENAI_API_KEY'] = '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'

st.title("MCQ Generator")


llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo")


topic = st.text_input("Enter a topic for the quiz:")


num_questions = st.number_input("Enter the number of questions:", min_value=1, max_value=10, value=2)



def parse_questions(response_text):
    questions = re.findall(r'Question\s\d+: (.*?)\nCHOICE_A:', response_text, re.DOTALL)
    options = re.findall(r'(CHOICE_[A-D]: [^\n]+)', response_text)
    answers = re.findall(r'Answer: ([A-D])', response_text)

    # Ensure the length of questions and answers is the same
    if len(questions) != len(answers):
        raise ValueError("The number of questions does not match the number of answers.")


    combined = []
    for i, (question, answer) in enumerate(zip(questions, answers)):
        question_options = options[i * 4:(i + 1) * 4]
        combined.append((question, question_options, answer))

    return combined, answers



if st.button("Generate Questions"):
    if topic:

        prompt_template = f"""
        You are a teacher preparing questions for a quiz related to {topic}, 
        please generate {num_questions} multiple-choice questions (MCQs) with 4 options 
        and a corresponding answer letter based on {topic}.

        Example question:
        Question: question here
        CHOICE_A: choice here
        CHOICE_B: choice here
        CHOICE_C: choice here
        CHOICE_D: choice here
        Answer: A or B or C or D
        """
        llm_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))
        response = llm_chain({"topic": topic})


        if response and isinstance(response, dict):
            response_text = response.get('text', '')

            if response_text:

                parsed_questions, answers = parse_questions(response_text)


                for i, (question, options, answer) in enumerate(parsed_questions, 1):
                    st.markdown(f"#### Question {i}: {question}")
                    option_values = [opt.split(": ")[1] for opt in options]
                    st.radio(f"Select an option for Question {i}:", option_values, key=f"q{i}")
            else:
                st.error("The response does not contain text.")
        else:
            st.error("No response received or format is incorrect.")
    else:
        st.warning("Please enter a topic.")