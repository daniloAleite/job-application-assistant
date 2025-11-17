import re
from urllib import response
from langgraph.graph import StateGraph
from langchain_openai import OpenAI

from src.models.schemas import ApplicationStateSchema
from src.models.schemas import FeedbackResponse


# Function to analyze the job description and extract requirements
def analyze_job_description_node(state: ApplicationStateSchema, llm):
    # Create a prompt to extract job requirements from the job description
    prompt = (
        f"""
        Given the following job description, extract a concise list (bullet points) of the main requirements and skills requested.\n
        Job Description:\n{state.job_description}
        """
    )

    # Use the language model to complete the prompt
    response = llm.invoke(prompt)

    # Update the state with the extracted job requirements
    state.job_requirements = response

    # Return the updated state
    return state


# Function to generate a summary of the resume's skills and experiences
def generate_resume_node(state, llm):
    # Create a prompt to summarize the resume's skills and experiences
    prompt = (
        f"""
        Given the following resume, extract a concise list (bullet points) of the candidate's main skills and experiences.\n
        Resume:\n{state.resume}
        """
    )

    # Use the language model to complete the prompt
    response = llm.invoke(prompt)

    # Update the state with the summarized resume skills
    state.resume_skills = response

    # Return the updated state
    return state


# Function to generate feedback comparing job requirements and resume skills
def generate_feedback_node(state, llm):
    # Create a prompt to generate feedback based on job requirements and resume skills
    prompt = (
        f"""
        Given the following job requirements and the candidate's resume skills, provide detailed feedback on how well the candidate matches the job requirements. Highlight strengths and areas for improvement.\n
        Job Requirements:\n{state.job_requirements}\n
        Resume Skills:\n{state.resume_skills}
        """
    )

    # Use the language model to complete the prompt
    response = llm.invoke(prompt)

    try:
        # Split the response into feedback, cover letter suggestion, and resume improvements
        feedback, cover_letter, improvements = response.split("---")
    except Exception:
        # If splitting fails, assign the entire response to feedback and leave others empty
        feedback, cover_letter, improvements = response, "", ""

    # Update the state with the generated feedback and suggestions
    state.feedback = feedback.strip()
    state.cover_letter_suggestion = cover_letter.strip()
    state.resume_improvements = improvements.strip()

    # Return the updated state
    return state


def process_application(resume, job_description, settings):
    # Initialize the OpenAI LLM with the provided API key
    llm = OpenAI(openai_api_key=settings.openai_api_key)
    # Create the initial application state
    initial_state = ApplicationStateSchema(
        resume=resume,
        job_description=job_description,
    )
    # Initialize the state graph
    graph = StateGraph(state_schema=ApplicationStateSchema)
    graph.add_node("analyze_job_description", lambda s: analyze_job_description_node(
        s, llm))  # Add the analyze job description node
    # Add the generate resume node
    graph.add_node(
        "generate_resume", lambda s: generate_resume_node(s, llm))
    # Add the generate feedback node
    graph.add_node(
        "generate_feedback", lambda s: generate_feedback_node(s, llm))
    graph.add_edge("__start__", "analyze_job_description")
    # Add edge from analyze job description to generate resume
    graph.add_edge("analyze_job_description", "generate_resume")
    # Add edge from generate resume to generate feedback
    graph.add_edge("generate_resume", "generate_feedback")

    executable_graph = graph.compile()

    result_state = executable_graph.invoke(
        {"resume": resume, "job_description": job_description},
        exit_point="generate_feedback",
    )

    return FeedbackResponse(
        feedback=result_state.feedback,
        cover_letter_suggestion=result_state.cover_letter_suggestion,
        resume_improvements=result_state.resume_improvements
    )
