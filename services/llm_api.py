import os
import json
from openai import AzureOpenAI
from CRI_AI.config.config import (
    AZURE_OPENAI_ENDPOINT,  
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION
    )

# Configure Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

def summarize_and_tag(post_data):
    """
    Summarize a Teams post (including replies) and generate tags using Azure OpenAI.
    """

    text = post_data.get("body", {}).get("content", "")
    replies = " ".join([r["body"]["content"] for r in post_data.get("replies", [])])
    full_text = ("Post :: " + text + " Replies :: " + replies).strip()

    prompt = f"""
    You are given a Microsoft Teams conversation (post and replies).

    Conversation:
    {full_text}

    Your tasks:
        1. Write exactly one complete sentence that summarizes the conversation clearly and meaningfully so that anyone (even outside the team) can understand it. 
        - Do not use bullet points or fragments.
        - Keep it concise and human-readable.

        2. Assign 1–3 tags that categorize the topic of the conversation. 
        - You MUST choose only from the tag list below. 
        - If no suitable tag is found, return "others".
        
    Tag List: 
        Categories:
            - Pipelines & Build: [PR Wait Time, PR Completion Time, PR Last Iteration Reliability, PR Pipeline Experience, CI Pipeline Experience, Patch Pipeline Experience, PR, CI & Patch Pipeline Reliability, Build Reliability and Correctness, Build Infrastructure, Artifact Lead Time, Build & Dependencies, Pipeline Management, Publishing to NPM/Nuget]

            - Reliability & Performance: [Outer Loop Performance, Inner-Loop yarn start, CI Perf, Codespaces Reliability, Codespaces Stability, Deployment Pipeline Reliability, Test Automation, Flaky Test Detection & Triage, Non-Intentional Visual Diffs in PR, Live Site]

            - Developer Experience: [GitHub Copilot Usage, VS Code IntelliSense/Debugging Experience, Create New Packages, Getting Started with 1JS, 1JS Documentation, 1JS Onboarding, Deployment and AI-Assisted Development]

            - Operations & Incidents: [Monitoring & Alerting, Incident Handling, Retrospectives & Repair Items, Customer Reported Incidents (CRI)]

            - Security & Compliance: [Compliance and Security, Common Dependency Updates, Security Dependency Tooling]

            - Codespaces: [Codespaces, Pipelines & Dev Environments]
            
            - Miscellaneous: [AGILITY, SAD, OCE Rotation & Training, yarn start, yarn install, yarn fast, 1DAG, Others]
    
    Output format:  
    Very important Respond only in JSON structure as mentioned below without any additional text or formatting :
    {{
        "summary": "...",
        "tags": ["tag1", "tag2", "tag3"]
    }}
    """

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,   # this must match your deployed model name
        messages=[
            {"role": "system", "content": """
             
             You are an expert assistant that summarizes and classifies Microsoft Teams conversations. 
                Your goals: 
                1. Always produce a clear, single-sentence summary that captures the full meaning of the conversation (post + replies). 
                2. Act as a strict classifier: assign 1–3 tags only from the approved taxonomy of categories and tags provided. 
                3. Be deterministic and consistent in tagging — never invent new tags, never miss obvious matches, and prefer the most specific tag(s). 
                4. If none of the tags match, return "others". 
                5. Output only valid JSON as instructed — no explanations, no extra text. 
                
             """},
            
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        summary = result.get("summary", "")
        tags = result.get("tags", [])
    except Exception:
        summary = content[:200]
        tags = ["uncategorized"]

    return summary, tags
